[KSPAddon(KSPAddon.Startup.MainMenu, false)]
public class Modump : UnityEngine.MonoBehaviour
{
    public void Awake() {
        /* Initialize mod */
    }

    private string ExportBody(CelestialBody body, bool first=true, string primary="") {
        string json = first ? "" : ",\n";

        string name = body.name;
        // comment this line if Planet X is discovered and is inhabited by small green humanoids
        if (name == "Sun") {
            name = "Kerbol";
        }

        json += "\n\t\"" + name + "\": {";

        // general
        json += string.Format("\n\t\t\"gravitational_parameter\": {0:g16}", body.gravParameter);
        json += string.Format(",\n\t\t\"radius\": {0:g16}", body.Radius);
        if (!body.tidallyLocked) {
            json += string.Format(",\n\t\t\"rotational_period\": {0:g16}", body.rotationPeriod);
        }

        // atmosphere
        if (body.atmosphere) {
            json += string.Format(",\n\t\t\"pressure_scale_height\": {0:g16}", body.atmosphereScaleHeight *   1000);
            json += string.Format(",\n\t\t\"pressure_at_sea_level\": {0:g16}", body.atmosphereMultiplier  * 101325);
        }

        // orbit
        Orbit orbit = body.orbit;
        if (orbit != null) {
            json += ",\n\t\t\"orbit\": {";
            json += "\n\t\t\t\"primary\": \"" + primary + "\"";
            json += string.Format(",\n\t\t\t\"semi_major_axis\": {0:g16}",             orbit.semiMajorAxis);
            json += string.Format(",\n\t\t\t\"eccentricity\": {0:g7}",                 orbit.eccentricity);
            json += string.Format(",\n\t\t\t\"inclination\": {0:g16}",                 orbit.inclination         * System.Math.PI / 180);
            json += string.Format(",\n\t\t\t\"longitude_of_ascending_node\": {0:g16}", orbit.LAN                 * System.Math.PI / 180);
            json += string.Format(",\n\t\t\t\"argument_of_periapsis\": {0:g16}",       orbit.argumentOfPeriapsis * System.Math.PI / 180);
            json += string.Format(",\n\t\t\t\"mean_anomaly_at_epoch\": {0:g7}",        orbit.meanAnomalyAtEpoch);
            json += "\n\t\t}";
        }
        json += "\n\t}";

        // planets/moons/satellites
        foreach (CelestialBody satellite in body.orbitingBodies) {
            json += this.ExportBody(satellite, false, name);
        }

        return json;
    }

    public void Start() {
        string json = "{";
        CelestialBody kerbol = FlightGlobals.Bodies[0];
        json += this.ExportBody(kerbol);
        json += "\n}\n";

        using (System.IO.StreamWriter outfile = new System.IO.StreamWriter("dump.json")) {
            outfile.Write(json);
        }
    }
};
