import XCTest
@testable import AstroNumeric

/// Decodes real responses from the live /v2/charts routes (trimmed), so a change in
/// either side's field names shows up here instead of as an empty screen.
final class AdvancedChartModelsTests: XCTestCase {
    private func decode<T: Decodable>(_ type: T.Type, _ json: String) throws -> T {
        try JSONDecoder().decode(V2ApiResponse<T>.self, from: Data(json.utf8)).data
    }

    func testSolarArcChartDecodes() throws {
        let chart = try decode(AdvancedChartResponse.self, #"""
{"status":"success","data":{"planets":[{"name":"Sun","sign":"Pisces","degree":11.894,"absolute_degree":341.894,"ecliptic_latitude":0.000135,"house":1,"retrograde":false,"dignity":null,"natal_degree":294.5968},{"name":"Moon","sign":"Aquarius","degree":11.9132,"absolute_degree":311.9132,"ecliptic_latitude":4.714593,"house":12,"retrograde":false,"dignity":null,"natal_degree":264.616},{"name":"Mercury","sign":"Pisces","degree":8.2319,"absolute_degree":338.2319,"ecliptic_latitude":-1.821323,"house":12,"retrograde":false,"dignity":"fall","natal_degree":290.9347}],"aspects":[{"planet_a":"Moon (d)","planet_b":"Saturn","type":"sesquiquadrate","orb":0.04,"strength":0.981},{"planet_a":"Jupiter (d)","planet_b":"Saturn","type":"semi_sextile","orb":0.05,"strength":0.976},{"planet_a":"Pluto (d)","planet_b":"Sun","type":"semi_square","orb":0.55,"strength":0.859}],"metadata":{"chart_type":"solar_arc","natal_date":"1980-01-15","directed_to":"2026-10-06","solar_arc_degrees":47.2972,"age_years":46.72,"provider":"flatlib"}}}
"""#)
        XCTAssertFalse(chart.planets.isEmpty)
        XCTAssertNotNil(chart.metadata?.solarArcDegrees)
        XCTAssertEqual(chart.metadata?.directedTo, "2026-10-06")
        XCTAssertFalse(chart.aspects.isEmpty)
    }

    func testLunarReturnChartDecodesReturnTimeAndNatalMoon() throws {
        let chart = try decode(AdvancedChartResponse.self, #"""
{"status":"success","data":{"planets":[{"name":"Sun","sign":"Libra","degree":22.7336,"absolute_degree":202.7336,"ecliptic_latitude":-0.000116,"house":5,"retrograde":false,"dignity":"fall"},{"name":"Moon","sign":"Sagittarius","degree":24.6158,"absolute_degree":264.6158,"ecliptic_latitude":-4.568688,"house":6,"retrograde":false,"dignity":null},{"name":"Mercury","sign":"Scorpio","degree":17.3637,"absolute_degree":227.3637,"ecliptic_latitude":-3.11654,"house":5,"retrograde":false,"dignity":null}],"aspects":[{"planet_a":"Sun","planet_b":"Moon","type":"sextile","orb":1.88,"strength":0.712},{"planet_a":"Sun","planet_b":"Jupiter","type":"sextile","orb":0.62,"strength":1.072},{"planet_a":"Sun","planet_b":"North Node","type":"trine","orb":4.18,"strength":0.312}],"metadata":{"chart_type":"lunar_return","datetime":"2026-10-15T22:04:01-04:00","location":{"lat":40.7128,"lon":-74.006},"house_system":"Placidus","provider":"flatlib","natal_moon":{"sign":"Sagittarius","degree":24.616,"absolute_degree":264.616},"return_datetime_utc":"2026-10-16T02:04:01+00:00","return_datetime_local":"2026-10-15T22:04:01-04:00"}}}
"""#)
        XCTAssertEqual(chart.metadata?.returnLocal, "2026-10-15T22:04:01-04:00")
        XCTAssertEqual(chart.metadata?.natalMoonSign, "Sagittarius")
        XCTAssertNotNil(chart.metadata?.natalMoonDegree)
        XCTAssertFalse(chart.planets.isEmpty)
    }

    func testRelocationChartDecodes() throws {
        let chart = try decode(AdvancedChartResponse.self, #"""
{"status":"success","data":{"planets":[{"name":"Sun","sign":"Capricorn","degree":24.5968,"absolute_degree":294.5968,"ecliptic_latitude":0.000135,"house":8,"retrograde":false,"dignity":null},{"name":"Moon","sign":"Sagittarius","degree":24.616,"absolute_degree":264.616,"ecliptic_latitude":4.714593,"house":7,"retrograde":false,"dignity":null},{"name":"Mercury","sign":"Capricorn","degree":20.9347,"absolute_degree":290.9347,"ecliptic_latitude":-1.821323,"house":8,"retrograde":false,"dignity":null}],"aspects":[{"planet_a":"Sun","planet_b":"Moon","type":"semi_sextile","orb":0.02,"strength":1.387},{"planet_a":"Sun","planet_b":"Mercury","type":"conjunction","orb":3.66,"strength":0.71},{"planet_a":"Sun","planet_b":"Jupiter","type":"sesquiquadrate","orb":0.01,"strength":1.178}],"metadata":{"chart_type":"relocation","datetime":"1980-01-15T15:30:00+01:00","location":{"lat":6.5244,"lon":3.3792},"house_system":"Placidus","provider":"flatlib","natal_location":{"lat":40.7128,"lon":-74.006},"relocation_location":{"lat":6.5244,"lon":3.3792}}}}
"""#)
        XCTAssertFalse(chart.planets.isEmpty)
        XCTAssertNotNil(chart.planets.first?.house)
    }

    func testProfectionsDecode() throws {
        let data = try decode(ProfectionsResponse.self, #"""
{"status":"success","data":{"age":46,"ascendant_sign":"Pisces","annual_house":11,"annual_sign":"Capricorn","annual_lord":"Saturn","annual_focus":"Friends, allies, groups, and long-term goals","annual_lord_themes":"discipline, responsibility, restriction, and long-term building","monthly_house":7,"monthly_sign":"Virgo","monthly_lord":"Mercury","monthly_focus":"Partnerships, marriage, and open enemies","months_into_year":9,"interpretation":"Year 47 activates House 11: Friends, allies, groups, and long-term goals. Capricorn is the profected sign, so Saturn becomes the Time Lord for the year, bringing themes of discipline, responsibility, restriction, and long-term building. This month (month 9) sub-activates House 7: Partnerships, marriage, and open enemies."},"error":null,"message":null,"request_id":null,"timestamp":"2026-10-06T07:57:27.960608"}
"""#)
        XCTAssertEqual(data.annualHouse, (data.age % 12) + 1)
        XCTAssertFalse(data.interpretation.isEmpty)
    }

    func testDeclinationsDecodeOutOfBoundsAndParallels() throws {
        let data = try decode(DeclinationsResponse.self, #"""
{"status":"success","data":{"declinations":[{"name":"Sun","longitude":294.5968,"latitude":0.0001,"declination":-21.2058,"out_of_bounds":false},{"name":"Mercury","longitude":290.9347,"latitude":-1.8213,"declination":-23.6113,"out_of_bounds":true}],"parallels":[{"planet_a":"North Node","planet_b":"South Node","type":"contra_parallel","orb":0.0,"strength":1.0},{"planet_a":"Mars","planet_b":"Jupiter","type":"parallel","orb":0.026,"strength":0.978}]}}
"""#)
        XCTAssertEqual(data.declinations.first(where: { $0.name == "Mercury" })?.outOfBounds, true)
        XCTAssertEqual(data.declinations.first(where: { $0.name == "Sun" })?.outOfBounds, false)
        XCTAssertFalse(data.parallels.isEmpty)
    }

    func testFixedStarsDecode() throws {
        let stars = try decode([FixedStarConjunction].self, #"""
{"status":"success","data":[{"planet":"Pluto","star":"Spica","orb":2.429,"nature":"benefic","keywords":"brilliance, artistic gifts, success in arts and sciences","interpretation":"Pluto conjunct Spica (orb 2.43\u00b0): brilliance, artistic gifts, success in arts and sciences."},{"planet":"Pluto","star":"Arcturus","orb":2.829,"nature":"benefic","keywords":"pioneering spirit, wealth through journeys, renown","interpretation":"Pluto conjunct Arcturus (orb 2.83\u00b0): pioneering spirit, wealth through journeys, renown."}],"error":null,"message":null,"request_id":null,"timestamp":"2026-10-06T07:57:28.462953"}
"""#)
        XCTAssertEqual(stars.first?.star, "Spica")
        XCTAssertFalse(stars.first?.interpretation.isEmpty ?? true)
    }

    func testMissingFieldsDoNotHideTheChart() throws {
        let chart = try decode(AdvancedChartResponse.self, #"{"status":"success","data":{"planets":[{"name":"Sun","sign":"Aries","degree":1.5}]}}"#)
        XCTAssertEqual(chart.planets.count, 1)
        XCTAssertTrue(chart.aspects.isEmpty)
        XCTAssertNil(chart.metadata)
    }

    func testLocalISODayUsesThePickersOwnCalendarDay() {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = .current
        let noon = calendar.date(from: DateComponents(year: 2026, month: 10, day: 6, hour: 12))!
        XCTAssertEqual(noon.localISODay, "2026-10-06")
    }
}
