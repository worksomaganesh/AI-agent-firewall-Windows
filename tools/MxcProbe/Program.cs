using System.Reflection;
using System.Text.Json;
using Microsoft.Mxc.Sdk.V1;

static object Describe(object? value)
{
    if (value is null) return new { value = (string?)null };
    var type = value.GetType();
    var properties = type.GetProperties(BindingFlags.Instance | BindingFlags.Public)
        .Where(property => property.GetIndexParameters().Length == 0)
        .ToDictionary(
            property => property.Name,
            property =>
            {
                try
                {
                    var item = property.GetValue(value);
                    return item is null || item is string || item.GetType().IsPrimitive || item.GetType().IsEnum
                        ? item
                        : item.ToString();
                }
                catch (Exception error)
                {
                    return $"<unavailable: {error.GetType().Name}>";
                }
            });
    return new { type = type.FullName, properties };
}

var report = new Dictionary<string, object?>
{
    ["runtime"] = new
    {
        framework = System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription,
        os = System.Runtime.InteropServices.RuntimeInformation.OSDescription,
        architecture = System.Runtime.InteropServices.RuntimeInformation.ProcessArchitecture.ToString(),
        processArchitecture = Environment.Is64BitProcess ? "64-bit" : "32-bit"
    }
};

try
{
    report["platformSupport"] = Describe(MxcPlatform.GetPlatformSupport());
}
catch (Exception error)
{
    report["platformSupportError"] = new { type = error.GetType().FullName, message = error.Message };
}

try
{
    report["availableBackends"] = Describe(MxcPlatform.GetAvailableBackends());
}
catch (Exception error)
{
    report["availableBackendsError"] = new { type = error.GetType().FullName, message = error.Message };
}

try
{
    report["processContainerProbe"] = Describe(MxcContainer.Probe());
}
catch (Exception error)
{
    report["processContainerProbeError"] = new { type = error.GetType().FullName, message = error.Message };
}

Console.WriteLine(JsonSerializer.Serialize(report, new JsonSerializerOptions
{
    WriteIndented = true
}));
