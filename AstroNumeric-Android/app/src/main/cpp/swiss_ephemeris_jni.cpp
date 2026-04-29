#include <jni.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <ctime>
#include <iomanip>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

#include "swephexp.h"

namespace {

constexpr double kDegreesPerSign = 30.0;
constexpr double kFullCircle = 360.0;
constexpr int64_t kMillisPerMinute = 60LL * 1000LL;
constexpr int64_t kMillisPerHour = 60LL * kMillisPerMinute;
constexpr int64_t kMillisPerDay = 24LL * kMillisPerHour;
constexpr int kHourRefinementRange = 24;
constexpr int kMinuteRefinementRange = 60;
constexpr int kMinuteRefinementHalfWindow = 30;
constexpr double kExactAspectOrb = 1.0;
constexpr double kTriggerAspectOrb = 1.5;

const std::array<const char*, 12> kSigns = {
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
};

struct PlanetDefinition {
    int32 id;
    const char* name;
};

struct AspectDefinition {
    const char* name;
    double angle;
    double orb;
    const char* significance;
};

struct PlanetResult {
    std::string name;
    std::string sign;
    double degree_in_sign;
    double absolute_degree;
    int house;
    bool retrograde;
    std::optional<std::string> dignity;
};

struct PointResult {
    std::string name;
    std::string sign;
    double degree_in_sign;
    double absolute_degree;
    int house;
    bool retrograde;
    std::optional<std::string> chart_type;
};

struct HouseResult {
    int house;
    std::string sign;
    double degree_in_sign;
    double absolute_degree;
};

struct AspectResult {
    std::string planet_a;
    std::string planet_b;
    std::string type;
    double orb;
    double strength;
};

struct ExactTransitResult {
    std::string transit_planet;
    std::string natal_point;
    std::string aspect;
    int64_t exact_epoch_millis;
    double orb;
    bool is_applying;
    std::string significance;
    std::string interpretation;
};

struct NatalPointInput {
    std::string name;
    double degree;
};

const std::array<PlanetDefinition, 10> kChartPlanets = {{
    {SE_SUN, "Sun"},
    {SE_MOON, "Moon"},
    {SE_MERCURY, "Mercury"},
    {SE_VENUS, "Venus"},
    {SE_MARS, "Mars"},
    {SE_JUPITER, "Jupiter"},
    {SE_SATURN, "Saturn"},
    {SE_URANUS, "Uranus"},
    {SE_NEPTUNE, "Neptune"},
    {SE_PLUTO, "Pluto"},
}};

const std::array<PlanetDefinition, 2> kChartPoints = {{
    {SE_MEAN_NODE, "North Node"},
    {SE_CHIRON, "Chiron"},
}};

const std::array<PlanetDefinition, 6> kTransitPlanets = {{
    {SE_MARS, "Mars"},
    {SE_JUPITER, "Jupiter"},
    {SE_SATURN, "Saturn"},
    {SE_URANUS, "Uranus"},
    {SE_NEPTUNE, "Neptune"},
    {SE_PLUTO, "Pluto"},
}};

const std::array<AspectDefinition, 6> kChartAspects = {{
    {"conjunction", 0.0, 8.0, "major"},
    {"opposition", 180.0, 8.0, "major"},
    {"trine", 120.0, 8.0, "major"},
    {"square", 90.0, 7.0, "major"},
    {"sextile", 60.0, 6.0, "minor"},
    {"quincunx", 150.0, 3.0, "minor"},
}};

const std::array<AspectDefinition, 5> kTransitAspects = {{
    {"conjunction", 0.0, kTriggerAspectOrb, "major"},
    {"opposition", 180.0, kTriggerAspectOrb, "major"},
    {"trine", 120.0, kTriggerAspectOrb, "major"},
    {"square", 90.0, kTriggerAspectOrb, "major"},
    {"sextile", 60.0, kTriggerAspectOrb, "minor"},
}};

std::mutex g_swiss_mutex;

std::optional<std::string> dignity_for(const std::string& planet, const std::string& sign) {
    if (planet == "Sun") {
        if (sign == "Leo") return "domicile";
        if (sign == "Aries") return "exaltation";
        if (sign == "Aquarius") return "detriment";
        if (sign == "Libra") return "fall";
    } else if (planet == "Moon") {
        if (sign == "Cancer") return "domicile";
        if (sign == "Taurus") return "exaltation";
        if (sign == "Capricorn") return "detriment";
        if (sign == "Scorpio") return "fall";
    } else if (planet == "Mercury") {
        if (sign == "Gemini" || sign == "Virgo") return "domicile";
        if (sign == "Sagittarius") return "detriment";
        if (sign == "Pisces") return "fall";
    } else if (planet == "Venus") {
        if (sign == "Taurus" || sign == "Libra") return "domicile";
        if (sign == "Pisces") return "exaltation";
        if (sign == "Aries" || sign == "Scorpio") return "detriment";
        if (sign == "Virgo") return "fall";
    } else if (planet == "Mars") {
        if (sign == "Aries" || sign == "Scorpio") return "domicile";
        if (sign == "Capricorn") return "exaltation";
        if (sign == "Taurus" || sign == "Libra") return "detriment";
        if (sign == "Cancer") return "fall";
    } else if (planet == "Jupiter") {
        if (sign == "Sagittarius" || sign == "Pisces") return "domicile";
        if (sign == "Cancer") return "exaltation";
        if (sign == "Gemini" || sign == "Virgo") return "detriment";
        if (sign == "Capricorn") return "fall";
    } else if (planet == "Saturn") {
        if (sign == "Capricorn" || sign == "Aquarius") return "domicile";
        if (sign == "Libra") return "exaltation";
        if (sign == "Cancer" || sign == "Leo") return "detriment";
        if (sign == "Aries") return "fall";
    } else if (planet == "Uranus") {
        if (sign == "Aquarius") return "domicile";
    } else if (planet == "Neptune") {
        if (sign == "Pisces") return "domicile";
    } else if (planet == "Pluto") {
        if (sign == "Scorpio") return "domicile";
    }
    return std::nullopt;
}

double normalize_degrees(double degrees) {
    double normalized = std::fmod(degrees, kFullCircle);
    return normalized >= 0.0 ? normalized : normalized + kFullCircle;
}

double local_degree(double absolute_degrees) {
    return std::fmod(normalize_degrees(absolute_degrees), kDegreesPerSign);
}

double angular_difference(double first, double second) {
    double difference = std::fabs(first - second);
    return difference > 180.0 ? kFullCircle - difference : difference;
}

double normalized_orb(double first, double second, double aspect_angle) {
    return std::fabs(angular_difference(first, second) - aspect_angle);
}

std::string sign_for(double absolute_degrees) {
    int sign_index = static_cast<int>(normalize_degrees(absolute_degrees) / kDegreesPerSign) % 12;
    return kSigns[sign_index];
}

int house_system_code(const std::string& house_system) {
    if (house_system == "Koch") return 'K';
    if (house_system == "Equal") return 'E';
    if (house_system == "Whole Sign") return 'W';
    if (house_system == "Campanus") return 'C';
    if (house_system == "Regiomontanus") return 'R';
    return 'P';
}

std::string escape_json(const std::string& value) {
    std::ostringstream escaped;
    for (char character : value) {
        switch (character) {
            case '\\': escaped << "\\\\"; break;
            case '"': escaped << "\\\""; break;
            case '\n': escaped << "\\n"; break;
            case '\r': escaped << "\\r"; break;
            case '\t': escaped << "\\t"; break;
            default:
                if (static_cast<unsigned char>(character) < 0x20) {
                    escaped << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                            << static_cast<int>(static_cast<unsigned char>(character))
                            << std::dec << std::setfill(' ');
                } else {
                    escaped << character;
                }
        }
    }
    return escaped.str();
}

std::string format_decimal(double value, int precision) {
    std::ostringstream stream;
    stream << std::fixed << std::setprecision(precision) << value;
    return stream.str();
}

void append_json_string(std::ostringstream& output, const std::string& value) {
    output << '"' << escape_json(value) << '"';
}

void append_json_optional_string(std::ostringstream& output, const std::optional<std::string>& value) {
    if (value.has_value()) {
        append_json_string(output, value.value());
    } else {
        output << "null";
    }
}

void throw_illegal_state(JNIEnv* env, const std::string& message) {
    jclass exception_class = env->FindClass("java/lang/IllegalStateException");
    if (exception_class != nullptr) {
        env->ThrowNew(exception_class, message.c_str());
    }
}

std::string jstring_to_string(JNIEnv* env, jstring value) {
    if (value == nullptr) {
        return std::string();
    }
    const char* chars = env->GetStringUTFChars(value, nullptr);
    std::string result(chars == nullptr ? "" : chars);
    env->ReleaseStringUTFChars(value, chars);
    return result;
}

void set_ephemeris_path(const std::string& path) {
    swe_set_ephe_path(const_cast<char*>(path.c_str()));
}

double julian_day_from_epoch_millis(int64_t epoch_millis) {
    std::time_t epoch_seconds = static_cast<std::time_t>(epoch_millis / 1000LL);
    int64_t millis_remainder = epoch_millis % 1000LL;
    std::tm utc_tm{};
    gmtime_r(&epoch_seconds, &utc_tm);
    double hour = static_cast<double>(utc_tm.tm_hour)
        + static_cast<double>(utc_tm.tm_min) / 60.0
        + (static_cast<double>(utc_tm.tm_sec) + static_cast<double>(millis_remainder) / 1000.0) / 3600.0;
    return swe_julday(
        static_cast<int32>(utc_tm.tm_year + 1900),
        static_cast<int32>(utc_tm.tm_mon + 1),
        static_cast<int32>(utc_tm.tm_mday),
        hour,
        SE_GREG_CAL
    );
}

std::string iso_utc_string(int64_t epoch_millis) {
    std::time_t epoch_seconds = static_cast<std::time_t>(epoch_millis / 1000LL);
    std::tm utc_tm{};
    gmtime_r(&epoch_seconds, &utc_tm);
    std::ostringstream stream;
    stream << std::put_time(&utc_tm, "%Y-%m-%dT%H:%M:%SZ");
    return stream.str();
}

double calculate_longitude(double julian_day, int32 planet_id, bool* retrograde = nullptr) {
    double xx[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
    char serr[256] = {0};
    int result = swe_calc_ut(julian_day, planet_id, SEFLG_SWIEPH | SEFLG_SPEED, xx, serr);
    if (result < 0) {
        throw std::runtime_error(serr[0] == '\0' ? "Swiss Ephemeris planet calculation failed." : serr);
    }
    if (retrograde != nullptr) {
        *retrograde = xx[3] < 0.0;
    }
    return normalize_degrees(xx[0]);
}

int house_for_longitude(double longitude, const std::vector<HouseResult>& houses) {
    if (houses.size() != 12) {
        return 1;
    }
    for (size_t index = 0; index < houses.size(); ++index) {
        double start = houses[index].absolute_degree;
        double end = houses[(index + 1) % houses.size()].absolute_degree;
        if (start > end) {
            if (longitude >= start || longitude < end) {
                return static_cast<int>(index) + 1;
            }
        } else if (longitude >= start && longitude < end) {
            return static_cast<int>(index) + 1;
        }
    }
    return 1;
}

std::vector<HouseResult> calculate_houses(double julian_day, double latitude, double longitude, const std::string& house_system) {
    std::vector<HouseResult> houses;
    houses.reserve(12);
    double cusps[13] = {0.0};
    double ascmc[10] = {0.0};

    swe_houses(julian_day, latitude, longitude, house_system_code(house_system), cusps, ascmc);

    for (int house = 1; house <= 12; ++house) {
        double absolute_degree = normalize_degrees(cusps[house]);
        houses.push_back(HouseResult{
            house,
            sign_for(absolute_degree),
            local_degree(absolute_degree),
            absolute_degree,
        });
    }
    return houses;
}

std::vector<PlanetResult> calculate_planets(double julian_day, const std::vector<HouseResult>& houses) {
    std::vector<PlanetResult> planets;
    planets.reserve(kChartPlanets.size());

    for (const auto& planet : kChartPlanets) {
        bool retrograde = false;
        double absolute_degree = calculate_longitude(julian_day, planet.id, &retrograde);
        std::string sign = sign_for(absolute_degree);
        planets.push_back(PlanetResult{
            planet.name,
            sign,
            local_degree(absolute_degree),
            absolute_degree,
            house_for_longitude(absolute_degree, houses),
            retrograde,
            dignity_for(planet.name, sign),
        });
    }

    return planets;
}

PointResult make_point(const std::string& name, double absolute_degree, const std::vector<HouseResult>& houses, bool retrograde = false, std::optional<std::string> chart_type = std::nullopt) {
    return PointResult{
        name,
        sign_for(absolute_degree),
        local_degree(absolute_degree),
        normalize_degrees(absolute_degree),
        house_for_longitude(normalize_degrees(absolute_degree), houses),
        retrograde,
        chart_type,
    };
}

std::vector<PointResult> calculate_points(
    double julian_day,
    double latitude,
    double longitude,
    const std::string& house_system,
    const std::vector<HouseResult>& houses,
    const std::vector<PlanetResult>& planets
) {
    std::vector<PointResult> points;
    points.reserve(6);

    double cusps[13] = {0.0};
    double ascmc[10] = {0.0};
    swe_houses(julian_day, latitude, longitude, house_system_code(house_system), cusps, ascmc);

    points.push_back(make_point("Ascendant", ascmc[0], houses));
    points.push_back(make_point("Midheaven", ascmc[1], houses));

    for (const auto& point : kChartPoints) {
        bool retrograde = false;
        double absolute_degree = calculate_longitude(julian_day, point.id, &retrograde);
        points.push_back(make_point(point.name, absolute_degree, houses, retrograde));
    }

    auto north_node = std::find_if(points.begin(), points.end(), [](const PointResult& point) {
        return point.name == "North Node";
    });
    if (north_node != points.end()) {
        points.push_back(make_point("South Node", north_node->absolute_degree + 180.0, houses, north_node->retrograde));
    }

    auto sun = std::find_if(planets.begin(), planets.end(), [](const PlanetResult& planet) { return planet.name == "Sun"; });
    auto moon = std::find_if(planets.begin(), planets.end(), [](const PlanetResult& planet) { return planet.name == "Moon"; });
    if (sun != planets.end() && moon != planets.end()) {
        double ascendant = ascmc[0];
        double day_delta = normalize_degrees(sun->absolute_degree - ascendant);
        bool is_day_chart = day_delta >= 180.0;
        double fortune = is_day_chart
            ? normalize_degrees(ascendant + moon->absolute_degree - sun->absolute_degree)
            : normalize_degrees(ascendant + sun->absolute_degree - moon->absolute_degree);
        points.push_back(make_point("Part of Fortune", fortune, houses, false, is_day_chart ? std::optional<std::string>("day") : std::optional<std::string>("night")));
    }

    return points;
}

std::vector<AspectResult> calculate_aspects(
    const std::vector<PlanetResult>& planets,
    const std::vector<PointResult>& points
) {
    struct AspectBody {
        std::string name;
        double absolute_degree;
    };

    std::vector<AspectBody> bodies;
    bodies.reserve(planets.size() + 2);
    for (const auto& planet : planets) {
        bodies.push_back(AspectBody{planet.name, planet.absolute_degree});
    }
    for (const auto& point : points) {
        if (point.name == "Ascendant" || point.name == "Midheaven") {
            bodies.push_back(AspectBody{point.name, point.absolute_degree});
        }
    }

    std::vector<AspectResult> aspects;
    for (size_t first_index = 0; first_index < bodies.size(); ++first_index) {
        for (size_t second_index = first_index + 1; second_index < bodies.size(); ++second_index) {
            double difference = angular_difference(bodies[first_index].absolute_degree, bodies[second_index].absolute_degree);
            for (const auto& aspect_definition : kChartAspects) {
                double orb = std::fabs(difference - aspect_definition.angle);
                if (orb <= aspect_definition.orb) {
                    aspects.push_back(AspectResult{
                        bodies[first_index].name,
                        bodies[second_index].name,
                        aspect_definition.name,
                        orb,
                        1.0 - (orb / aspect_definition.orb),
                    });
                    break;
                }
            }
        }
    }
    return aspects;
}

std::string build_natal_chart_json(
    const std::string& name,
    const std::string& date_of_birth,
    const std::string& time_of_birth,
    bool birth_time_assumed,
    const std::string& data_quality,
    const std::string& timezone,
    const std::string& house_system,
    const std::vector<PlanetResult>& planets,
    const std::vector<PointResult>& points,
    const std::vector<HouseResult>& houses,
    const std::vector<AspectResult>& aspects
) {
    std::ostringstream output;
    output << '{';

    output << "\"planets\":[";
    for (size_t index = 0; index < planets.size(); ++index) {
        if (index > 0) output << ',';
        const auto& planet = planets[index];
        output << '{';
        output << "\"name\":"; append_json_string(output, planet.name); output << ',';
        output << "\"sign\":"; append_json_string(output, planet.sign); output << ',';
        output << "\"degree\":" << format_decimal(planet.degree_in_sign, 4) << ',';
        output << "\"absolute_degree\":" << format_decimal(planet.absolute_degree, 4) << ',';
        output << "\"house\":" << planet.house << ',';
        output << "\"retrograde\":" << (planet.retrograde ? "true" : "false") << ',';
        output << "\"dignity\":"; append_json_optional_string(output, planet.dignity);
        output << '}';
    }
    output << "],";

    output << "\"points\":[";
    for (size_t index = 0; index < points.size(); ++index) {
        if (index > 0) output << ',';
        const auto& point = points[index];
        output << '{';
        output << "\"name\":"; append_json_string(output, point.name); output << ',';
        output << "\"sign\":"; append_json_string(output, point.sign); output << ',';
        output << "\"degree\":" << format_decimal(point.degree_in_sign, 4) << ',';
        output << "\"absolute_degree\":" << format_decimal(point.absolute_degree, 4) << ',';
        output << "\"house\":" << point.house << ',';
        output << "\"retrograde\":" << (point.retrograde ? "true" : "false") << ',';
        output << "\"chart_type\":"; append_json_optional_string(output, point.chart_type);
        output << '}';
    }
    output << "],";

    output << "\"houses\":[";
    for (size_t index = 0; index < houses.size(); ++index) {
        if (index > 0) output << ',';
        const auto& house = houses[index];
        output << '{';
        output << "\"house\":" << house.house << ',';
        output << "\"sign\":"; append_json_string(output, house.sign); output << ',';
        output << "\"degree\":" << format_decimal(house.degree_in_sign, 4);
        output << '}';
    }
    output << "],";

    output << "\"aspects\":[";
    for (size_t index = 0; index < aspects.size(); ++index) {
        if (index > 0) output << ',';
        const auto& aspect = aspects[index];
        output << '{';
        output << "\"planet_a\":"; append_json_string(output, aspect.planet_a); output << ',';
        output << "\"planet_b\":"; append_json_string(output, aspect.planet_b); output << ',';
        output << "\"type\":"; append_json_string(output, aspect.type); output << ',';
        output << "\"orb\":" << format_decimal(aspect.orb, 4) << ',';
        output << "\"strength\":" << format_decimal(aspect.strength, 4);
        output << '}';
    }
    output << "],";

    output << "\"metadata\":{";
    output << "\"name\":"; append_json_string(output, name); output << ',';
    output << "\"date_of_birth\":"; append_json_string(output, date_of_birth); output << ',';
    output << "\"time_of_birth\":"; append_json_string(output, time_of_birth); output << ',';
    output << "\"birth_time_assumed\":" << (birth_time_assumed ? "true" : "false") << ',';
    output << "\"assumed_time_of_birth\":";
    append_json_optional_string(output, birth_time_assumed ? std::optional<std::string>(time_of_birth) : std::nullopt);
    output << ',';
    output << "\"data_quality\":"; append_json_string(output, data_quality); output << ',';
    output << "\"timezone\":"; append_json_string(output, timezone); output << ',';
    output << "\"house_system\":"; append_json_string(output, house_system);
    output << "}}";

    return output.str();
}

std::optional<std::pair<int64_t, double>> refine_exact_transit(
    int32 transit_planet_id,
    double natal_degree,
    double aspect_angle,
    int64_t start_epoch_millis
) {
    int64_t best_epoch_millis = start_epoch_millis;
    double best_orb = 999.0;

    for (int hour_offset = 0; hour_offset < kHourRefinementRange; ++hour_offset) {
        int64_t candidate_epoch_millis = start_epoch_millis + static_cast<int64_t>(hour_offset) * kMillisPerHour;
        double orb = normalized_orb(
            calculate_longitude(julian_day_from_epoch_millis(candidate_epoch_millis), transit_planet_id),
            natal_degree,
            aspect_angle
        );
        if (orb < best_orb) {
            best_orb = orb;
            best_epoch_millis = candidate_epoch_millis;
        }
    }

    int64_t minute_window_start = best_epoch_millis - static_cast<int64_t>(kMinuteRefinementHalfWindow) * kMillisPerMinute;
    for (int minute_offset = 0; minute_offset < kMinuteRefinementRange; ++minute_offset) {
        int64_t candidate_epoch_millis = minute_window_start + static_cast<int64_t>(minute_offset) * kMillisPerMinute;
        double orb = normalized_orb(
            calculate_longitude(julian_day_from_epoch_millis(candidate_epoch_millis), transit_planet_id),
            natal_degree,
            aspect_angle
        );
        if (orb < best_orb) {
            best_orb = orb;
            best_epoch_millis = candidate_epoch_millis;
        }
    }

    if (best_orb < kExactAspectOrb) {
        return std::make_pair(best_epoch_millis, best_orb);
    }
    return std::nullopt;
}

std::vector<NatalPointInput> extract_natal_points(JNIEnv* env, jobjectArray natal_names, jdoubleArray natal_degrees) {
    std::vector<NatalPointInput> natal_points;
    jsize name_count = env->GetArrayLength(natal_names);
    jsize degree_count = env->GetArrayLength(natal_degrees);
    if (name_count != degree_count) {
        throw std::runtime_error("Natal point names and degrees must be the same length.");
    }

    std::vector<jdouble> degree_buffer(static_cast<size_t>(degree_count));
    env->GetDoubleArrayRegion(natal_degrees, 0, degree_count, degree_buffer.data());

    natal_points.reserve(static_cast<size_t>(name_count));
    for (jsize index = 0; index < name_count; ++index) {
        auto* java_name = static_cast<jstring>(env->GetObjectArrayElement(natal_names, index));
        natal_points.push_back(NatalPointInput{jstring_to_string(env, java_name), degree_buffer[static_cast<size_t>(index)]});
        env->DeleteLocalRef(java_name);
    }
    return natal_points;
}

std::string build_exact_transits_json(const std::vector<ExactTransitResult>& transits) {
    std::ostringstream output;
    output << '[';
    for (size_t index = 0; index < transits.size(); ++index) {
        if (index > 0) output << ',';
        const auto& transit = transits[index];
        output << '{';
        output << "\"transit_planet\":"; append_json_string(output, transit.transit_planet); output << ',';
        output << "\"natal_point\":"; append_json_string(output, transit.natal_point); output << ',';
        output << "\"aspect\":"; append_json_string(output, transit.aspect); output << ',';
        output << "\"exact_date\":"; append_json_string(output, iso_utc_string(transit.exact_epoch_millis)); output << ',';
        output << "\"orb\":" << format_decimal(transit.orb, 2) << ',';
        output << "\"is_applying\":" << (transit.is_applying ? "true" : "false") << ',';
        output << "\"significance\":"; append_json_string(output, transit.significance); output << ',';
        output << "\"interpretation\":"; append_json_string(output, transit.interpretation);
        output << '}';
    }
    output << ']';
    return output.str();
}

std::vector<ExactTransitResult> calculate_exact_transits(
    const std::vector<NatalPointInput>& natal_points,
    int days_ahead,
    int64_t start_epoch_millis
) {
    std::vector<ExactTransitResult> results;

    for (int day_offset = 0; day_offset < std::max(days_ahead, 0); ++day_offset) {
        int64_t scan_epoch_millis = start_epoch_millis + static_cast<int64_t>(day_offset) * kMillisPerDay;

        for (const auto& transit_planet : kTransitPlanets) {
            double transit_degree = calculate_longitude(julian_day_from_epoch_millis(scan_epoch_millis), transit_planet.id);
            for (const auto& natal_point : natal_points) {
                if (natal_point.name == transit_planet.name) {
                    continue;
                }
                for (const auto& aspect : kTransitAspects) {
                    double orb = normalized_orb(transit_degree, natal_point.degree, aspect.angle);
                    if (orb > aspect.orb) {
                        continue;
                    }

                    auto refined = refine_exact_transit(
                        transit_planet.id,
                        natal_point.degree,
                        aspect.angle,
                        scan_epoch_millis
                    );
                    if (!refined.has_value()) {
                        continue;
                    }

                    int64_t exact_epoch_millis = refined->first;
                    double exact_orb = refined->second;

                    bool duplicate = std::any_of(results.begin(), results.end(), [&](const ExactTransitResult& existing) {
                        return existing.transit_planet == transit_planet.name &&
                            existing.natal_point == natal_point.name &&
                            existing.aspect == aspect.name &&
                            std::llabs(existing.exact_epoch_millis - exact_epoch_millis) < kMillisPerDay;
                    });
                    if (duplicate) {
                        continue;
                    }

                    double next_day_orb = normalized_orb(
                        calculate_longitude(julian_day_from_epoch_millis(exact_epoch_millis + kMillisPerDay), transit_planet.id),
                        natal_point.degree,
                        aspect.angle
                    );

                    results.push_back(ExactTransitResult{
                        transit_planet.name,
                        natal_point.name,
                        aspect.name,
                        exact_epoch_millis,
                        exact_orb,
                        next_day_orb > exact_orb,
                        aspect.significance,
                        "Calculated on-device with Swiss Ephemeris.",
                    });
                }
            }
        }
    }

    std::sort(results.begin(), results.end(), [](const ExactTransitResult& first, const ExactTransitResult& second) {
        return first.exact_epoch_millis < second.exact_epoch_millis;
    });

    return results;
}

}  // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_com_astromeric_android_core_ephemeris_SwissEphemerisBridge_nativeProbe(
    JNIEnv* env,
    jobject /* thiz */,
    jstring ephemeris_path
) {
    std::lock_guard<std::mutex> lock(g_swiss_mutex);
    set_ephemeris_path(jstring_to_string(env, ephemeris_path));
    return env->NewStringUTF("Swiss bridge ready");
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_astromeric_android_core_ephemeris_SwissEphemerisBridge_nativeCalculateNatalChart(
    JNIEnv* env,
    jobject /* thiz */,
    jstring ephemeris_path,
    jstring name,
    jstring date_of_birth,
    jstring time_of_birth,
    jboolean birth_time_assumed,
    jstring data_quality,
    jstring timezone,
    jstring house_system,
    jdouble latitude,
    jdouble longitude,
    jint utc_year,
    jint utc_month,
    jint utc_day,
    jdouble utc_hour
) {
    try {
        std::lock_guard<std::mutex> lock(g_swiss_mutex);
        set_ephemeris_path(jstring_to_string(env, ephemeris_path));

        double julian_day = swe_julday(utc_year, utc_month, utc_day, utc_hour, SE_GREG_CAL);
        std::string house_system_value = jstring_to_string(env, house_system);
        auto houses = calculate_houses(julian_day, latitude, longitude, house_system_value);
        auto planets = calculate_planets(julian_day, houses);
        auto points = calculate_points(julian_day, latitude, longitude, house_system_value, houses, planets);
        auto aspects = calculate_aspects(planets, points);

        std::string json = build_natal_chart_json(
            jstring_to_string(env, name),
            jstring_to_string(env, date_of_birth),
            jstring_to_string(env, time_of_birth),
            birth_time_assumed == JNI_TRUE,
            jstring_to_string(env, data_quality),
            jstring_to_string(env, timezone),
            house_system_value,
            planets,
            points,
            houses,
            aspects
        );

        return env->NewStringUTF(json.c_str());
    } catch (const std::exception& exception) {
        throw_illegal_state(env, exception.what());
        return nullptr;
    }
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_astromeric_android_core_ephemeris_SwissEphemerisBridge_nativeFindUpcomingExactTransits(
    JNIEnv* env,
    jobject /* thiz */,
    jstring ephemeris_path,
    jobjectArray natal_names,
    jdoubleArray natal_degrees,
    jint days_ahead,
    jlong start_epoch_millis
) {
    try {
        std::lock_guard<std::mutex> lock(g_swiss_mutex);
        set_ephemeris_path(jstring_to_string(env, ephemeris_path));

        auto natal_points = extract_natal_points(env, natal_names, natal_degrees);
        auto exact_transits = calculate_exact_transits(natal_points, days_ahead, start_epoch_millis);
        std::string json = build_exact_transits_json(exact_transits);
        return env->NewStringUTF(json.c_str());
    } catch (const std::exception& exception) {
        throw_illegal_state(env, exception.what());
        return nullptr;
    }
}