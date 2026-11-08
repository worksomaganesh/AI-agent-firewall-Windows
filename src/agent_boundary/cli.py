"""CLI for the Windows-first agent-boundary policy and evidence core."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Annotated
import typer
from rich.console import Console
from rich.table import Table
from agent_boundary import __version__
from agent_boundary.audit.report import generate_session_report
from agent_boundary.audit.verifier import verify_audit_log
from agent_boundary.exit_codes import ExitCode
from agent_boundary.policy.engine import ActionRequest, PolicyEngine
from agent_boundary.policy.parser import PolicyValidationError, load_policy
from agent_boundary.policy.schema import Decision
from agent_boundary.simulator import load_scenario, run_simulation

app = typer.Typer(name="agent-boundary", help="Windows-first local security supervisor for AI coding agents (enforcement backend under development).", add_completion=False, no_args_is_help=True)
console = Console()

def _version_callback(value: bool) -> None:
    if value:
        console.print(f"agent-boundary Windows {__version__}")
        raise typer.Exit(code=int(ExitCode.OK))

@app.callback()
def main(version: Annotated[bool | None, typer.Option("--version", "-V", callback=_version_callback, is_eager=True)] = None) -> None:
    """agent-boundary Windows CLI."""

@app.command("validate-policy")
def validate_policy_cmd(policy_path: Annotated[Path, typer.Argument(help="Windows policy YAML file.")]) -> None:
    """Validate the strict v1.0 policy schema."""
    try:
        doc = load_policy(policy_path)
    except PolicyValidationError as exc:
        console.print(f"[bold red]POLICY VALIDATION FAILED:[/bold red] {exc}")
        raise typer.Exit(code=int(ExitCode.CONFIG_OR_POLICY_ERROR)) from exc
    counts = {name: sum(len(getattr(getattr(doc, name), tier)) for tier in ("deny", "require_approval", "allow")) for name in ("filesystem", "commands", "network")}
    console.print(f"[bold green]VALID POLICY:[/bold green] {doc.policy_id} (schema={doc.schema_version}, default={doc.default_decision.value}, rules={counts})")

@app.command("evaluate")
def evaluate_cmd(policy: Annotated[Path, typer.Option("--policy", "-p")], category: Annotated[str, typer.Option("--category", "-c")], operation: Annotated[str, typer.Option("--operation", "-o")], target: Annotated[str, typer.Option("--target", "-t")]) -> None:
    """Evaluate one policy action; this command does not execute an OS operation."""
    try:
        doc = load_policy(policy)
    except PolicyValidationError as exc:
        console.print(f"[bold red]POLICY ERROR:[/bold red] {exc}")
        raise typer.Exit(code=int(ExitCode.CONFIG_OR_POLICY_ERROR)) from exc
    result = PolicyEngine(doc).evaluate(ActionRequest(category=category, operation=operation, target=target))
    console.print(f"[yellow]POLICY EVALUATION ONLY — NO OS EXECUTION[/yellow]\nDecision: {result.decision.value.upper()}\nRule: {result.matched_rule_id}\nTarget: {result.normalized_target}\nReason: {result.reason}")
    if result.decision is not Decision.ALLOW:
        raise typer.Exit(code=int(ExitCode.POLICY_DENIED))

@app.command("simulate")
def simulate_cmd(policy: Annotated[Path, typer.Option("--policy", "-p")], scenario: Annotated[Path, typer.Option("--scenario", "-s")], output_dir: Annotated[Path, typer.Option("--output-dir", "-d")]) -> None:
    """Run a deterministic mock-agent scenario; no process or network is launched."""
    try:
        doc = load_policy(policy)
        scen = load_scenario(scenario)
        summary = run_simulation(policy=doc, scenario=scen, output_dir=output_dir)
    except (PolicyValidationError, ValueError, OSError) as exc:
        console.print(f"[bold red]SIMULATION FAILED:[/bold red] {exc}")
        raise typer.Exit(code=int(ExitCode.CONFIG_OR_POLICY_ERROR)) from exc
    table = Table(title=f"Simulation: {summary.session_id}")
    for heading in ("Step", "Action", "Target", "Decision", "Rule"):
        table.add_column(heading)
    for step, result in summary.results:
        table.add_row(step.action_id, f"{step.category}:{step.operation}", step.target, result.decision.value.upper(), result.matched_rule_id)
    console.print("[yellow]SIMULATION MODE — NO WINDOWS OS ENFORCEMENT[/yellow]")
    console.print(table)
    console.print(f"Audit: {summary.audit_log_path}")
    console.print(f"Report: {summary.report_path}")
    console.print(f"Head hash: {summary.head_hash}")
    if summary.expectation_mismatches:
        for mismatch in summary.expectation_mismatches:
            console.print(f"[red]{mismatch}[/red]")
        raise typer.Exit(code=int(ExitCode.POLICY_DENIED))

@app.command("verify-audit")
def verify_audit_cmd(audit_path: Annotated[Path, typer.Argument()], expected_head_hash: Annotated[str | None, typer.Option("--expected-head-hash")] = None, require_hmac: Annotated[bool, typer.Option("--require-hmac")] = False) -> None:
    """Verify JSONL audit chain and optional HMAC signatures."""
    result = verify_audit_log(log_path=audit_path, expected_head_hash=expected_head_hash, require_hmac=require_hmac)
    for warning in result.warnings:
        console.print(f"[yellow]WARNING:[/yellow] {warning}")
    if not result.valid:
        for error in result.errors:
            console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=int(ExitCode.AUDIT_TAMPER_DETECTED))
    console.print(f"[green]AUDIT VERIFIED[/green] records={result.records_checked} head={result.head_hash} anchored={result.head_hash_anchored}")

@app.command("report")
def report_cmd(session_dir: Annotated[Path, typer.Argument()], output: Annotated[Path | None, typer.Option("--output", "-o")] = None) -> None:
    """Generate a human-readable session report."""
    try:
        report = generate_session_report(session_dir)
        if output is not None:
            output.write_text(report, encoding="utf-8")
            console.print(f"Report written: {output}")
        else:
            console.print(report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"[red]REPORT FAILED:[/red] {exc}")
        raise typer.Exit(code=int(ExitCode.CONFIG_OR_POLICY_ERROR)) from exc

if __name__ == "__main__":
    app()
