const calculatePercentage = require('./../CalculatePercent');

describe('calculatePercent', () => {

    // Helper function to generate string scenarios
    const generateScenario = (scenario) => {
        switch(scenario) {
            case "100% Plagiarism Sentences":
                let string = "exampl.es?tring";
                return [string, string, "sentences", "(?<=[.!?])\\s+", 100];
            case "100% Plagiarism Paragraphs":
                let stringline = "example\nstring";
                return [stringline,stringline, "paragraphs", "\n", 100];            
            case "0% Plagiarism Sentences":
                return ["a.a.a.aaaaaaa", "bbbb.b?b.bbbb",  "sentences", "(?<=[.!?])\\s+", 0];
            case "0% Plagiarism Paragraphs":
                return ["aaaa\naaaaaa", "bbbbb\nbb\nbb\nb", "paragraphs", "\n" ,0];
            case "50% Plagiarism Sentences":
                let word1S = "horse.";
                let word2S = "ros."
                return [word1S, word2S, "sentences", "(?<=[.!?])\\s+", 50];
            case "50% Plagiarism Paragraphs":
                let word1P = "horse\n";
                let word2P = "ros\n"
                return [word1P, word2P, "sentences", "(?<=[.!?])\\s+",  50];
            case "100% Plagiarism Long Sentence":
                let passage = "Climate change is among the most significant challenges facing humanity today. The rise in global temperatures, predominantly due to human activities, has profound implications for our environment. Glaciers are melting at an unprecedented rate, leading to rising sea levels. The increasing frequency of extreme weather events, such as hurricanes and droughts, is a testament to the changing climate. It's essential for nations to come together to address this pressing issue";
                return [passage, passage, "sentences", "(?<=[.!?])\\s+", 100];
            case "~36% Plagiarism Long Sentence":
                let passage1 = "One of the biggest challenges facing humanity in this era is climate change. Due to predominantly human activities, we see a notable rise in global temperatures. This has a deep impact on our environment. The melting glaciers are causing sea levels to rise at rates never seen before. Furthermore, we observe more frequent extreme weather conditions like hurricanes and prolonged droughts, which clearly shows the effects of a changing climate. It's crucial for countries worldwide to unite and tackle this urgent problem.";
                let passage2 = "Climate change is among the most significant challenges facing humanity today. The rise in global temperatures, predominantly due to human activities, has profound implications for our environment. Glaciers are melting at an unprecedented rate, leading to rising sea levels. The increasing frequency of extreme weather events, such as hurricanes and droughts, is a testament to the changing climate. It's essential for nations to come together to address this pressing issue.";
                return [passage1, passage2,"sentences", "(?<=[.!?])\\s+",  36.40740819140192];

            default:
                return ["", "", 0];
        }
    };

    // List of scenarios to test
    const scenarios = [
        "100% Plagiarism Sentences",
        "100% Plagiarism Paragraphs",
        "0% Plagiarism Sentences",
        "0% Plagiarism Paragraphs",
        "50% Plagiarism Sentences",
        "50% Plagiarism Paragraphs",
        "100% Plagiarism Long Sentence",
        "~36% Plagiarism Long Sentence"
    ];

    scenarios.forEach(scenario => {
        test(`${scenario}`, () => {
            const [str1, str2, type, delimiter, expected] = generateScenario(scenario);
            let similarity = 0;
            if( type == "sentences")
                similarity =  calculatePercentage.calculatePercentageChunks(str1, str2, delimiter)["overallSimilarity"];
            else if( type == "paragraphs")
                similarity = calculatePercentage.calculatePercentageChunks(str1, str2, delimiter)["overallSimilarity"];
            expect(similarity).toBe(expected);
        });
    });
});
