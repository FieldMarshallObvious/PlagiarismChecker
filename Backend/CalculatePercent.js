const distance = require('./LevenshteinDistance');

/**
 * ! Function: calculatePercentage
 * 
 * ? Description:
 *   This function calculates the similarity percentage between two texts based on the Levenshtein Distance.
 *   If the distance exceeds a given threshold, the similarity is set to 0%.
 * 
 * * Parameters:
 *  @param text1: The first text to compare.
 *  @param text2: The second text to compare.
 *  @param distanceThreshold (optional): The maximum allowable distance. Default is 1000.
 * 
 * * Returns:
 *   A number representing the similarity percentage between text1 and text2
 
 * ! Drawbacks:
 * 1. Memory Efficiency: The underlying Levenshtein Distance algorithm has O(m) space complexity, where m is the length of `text2`
 * 2. Lack of Context: The Levenshtein Distance algorithim considers textual closeness, not semantic similarity. 
 *                     Two different pieces of text could communicate the same idea but not be textually close.
 * 3. Case Sensitivity: If normalization of text is not done beforehand the cases of the text could affect the outcome.

 */

function calculatePercentage(text1, text2, distanceThreshold = 1000) {
    let distanceResult = distance(text1, text2, distanceThreshold);
    let strDist = distanceResult.distance;
    distanceTable = distanceResult.table;
    let strLength = Math.max(text1.length, text2.length);

    // Handle threshold exceeded scenario
    if (strDist > distanceThreshold) {
        return 0;
    }

    let similarity =  ((strLength - strDist)/strLength) * 100;

    return similarity;
}

/**
 * ! Function: calculatePercentageChunks
 * 
 * ? Description:
 *   This function calculates the similarity percentage between chunks of two texts. Chunks are determined 
 *   based on a regex pattern. For each chunk-pair, if the distance exceeds the given threshold, 
 *   the similarity is set to 0%.
 * 
 * * Parameters:
 * @param text1: The first text to be chunked and compared.
 * @param text2: The second text to be chunked and compared.
 * @param pattern: The regex pattern to determine chunks.
 * @param distanceThreshold (optional): The maximum allowable distance for each chunk. Default is 1000.
 * 
 * * Returns:
 *   An object containing:
 *   - chunkSimilarities: An array of similarity percentages for each chunk-pair.
 *   - overallSimilarity: The average similarity percentage of all chunk-pairs.
 * ! Drawbacks
 * 1. Arbitrary Chunks: Chunking is done based on a regex pattern, this could lead to some chunks being split 
 *                      arbitrarily not logically.
 * 2. Rechuncking: This function maps everything from `chunks1` to `chunks2`, this could lead to many redundant calculations
 *                 between similar chunks.
 * 3. Weighting Issues: All chunks are considered equal. In actual text this could not be the case, where some chunks 
 *                      of text might be more important than others
 * 4. Potential Skewed Results: The calculation works on the best combination for each chunk in `chunks1` from `chunks2`. 
 *                              As a result a chunk in `chunks1` might be a very good match for `chunks2`, skewing results.
 */

function calculatePercentageChunks(text1, text2, pattern, distanceThreshold = 1000) {
    const regexPattern = new RegExp(pattern);

    const chunks1 = text1.split(regexPattern).filter(chunk => chunk.trim() !== '');
    const chunks2 = text2.split(regexPattern).filter(chunk => chunk.trim() !== '');

    chunkSimilarities = new Array(chunks1.length);

    for(let i = 0; i < chunks1.length; i++ ) {
        let curSimilartiy = 0;
        for( let j = 0; j < chunks2.length; j++ ) {
            let strDist = distance(chunks1[i], chunks2[j], distanceThreshold).distance;
            let strLength = Math.max(chunks1[i].length, chunks2[j].length);

            // Handle threshold exceeded scenario
            if (strDist > distanceThreshold) {
                continue; // move on to the next chunk comparison
            }

            curSimilartiy =  Math.max(curSimilartiy, ((strLength - strDist)/strLength) * 100);
        }
        chunkSimilarities[i] = curSimilartiy
    }

    console


    const overallSimilarity = chunkSimilarities.reduce((sum, sim) => sum + sim, 0) / chunkSimilarities.length;
    
    return {
        newChunkSimilarities: chunkSimilarities, overallSimilarity: overallSimilarity
    };
}

module.exports = {
    calculatePercentage, calculatePercentageChunks
}