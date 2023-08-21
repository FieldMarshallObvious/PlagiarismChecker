const calculateDistance = require('./../LevenshteinDistance');

describe('calculateDistance', () => {

    // Helper function to generate string scenarios
    const generateScenario = (scenario) => {
        switch(scenario) {
            case "0 Distance":
                let string = "examplestring";
                return [string, string, 0];
            case "Full Length Distance":
                return ["aaaaaaaaaa", "bbbbbbbbbb", 10];
            case "3 Distance":
                let word1 = "horse";
                let word2 = "ros"
                return [word1, word2, 3];
            case "0 Distance Long":
                let passage = "Climate change is among the most significant challenges facing humanity today. The rise in global temperatures, predominantly due to human activities, has profound implications for our environment. Glaciers are melting at an unprecedented rate, leading to rising sea levels. The increasing frequency of extreme weather events, such as hurricanes and droughts, is a testament to the changing climate. It's essential for nations to come together to address this pressing issue";
                return [passage, passage, 0];
            case "308 Distance Long":
                let passage1 = "One of the biggest challenges facing humanity in this era is climate change. Due to predominantly human activities, we see a notable rise in global temperatures. This has a deep impact on our environment. The melting glaciers are causing sea levels to rise at rates never seen before. Furthermore, we observe more frequent extreme weather conditions like hurricanes and prolonged droughts, which clearly shows the effects of a changing climate. It's crucial for countries worldwide to unite and tackle this urgent problem.";
                let passage2 = "Climate change is among the most significant challenges facing humanity today. The rise in global temperatures, predominantly due to human activities, has profound implications for our environment. Glaciers are melting at an unprecedented rate, leading to rising sea levels. The increasing frequency of extreme weather events, such as hurricanes and droughts, is a testament to the changing climate. It's essential for nations to come together to address this pressing issue.";
                return [passage1, passage2, 308 ];

            default:
                return ["", "", 0];
        }
    };

    // List of scenarios to test
    const scenarios = [
        "0 Distance",
        "Full Length Distance",
        "0 Distance Long",
        "308 Distance Long"
    ];

    scenarios.forEach(scenario => {
        test(`${scenario}`, () => {
            const [str1, str2, expected] = generateScenario(scenario);
            const strDist = calculateDistance(str1, str2).distance;
            expect(strDist).toBe(expected);
        });
    });
});
