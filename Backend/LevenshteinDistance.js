/**
 * ! distance() Function 
 
 * * Description:
   This function calculates the Levenshtein distance between two strings.
   It determines the minimum number of edits (insertions, deletions, or substitutions) 
   required to change one string into the other.
 
 * * Parameters:
 * @param str1: The first string.
 * @param str2: The second string.
 * @param threshold: A limit for early computation termination.
 
 * * Returns:
 * The edit distance if it's within the threshold; 
 * otherwise returns `threshold + 1`.
 
 * ! Drawbacks:
 * 1. Limited Early Exit: Can be time-consuming for long strings with small differences.
 * 2. Scalability Concerns: Uses O(n*m) time where n,m is length of `str1` & `st2` respectively. 
 *    For very long texts this could be very expensive 
 * 2. Memory Consumption: Uses O(m) space where m is the length of `str2`.
 * 3. Fixed Costs: Assumes uniform costs for all edit operations.
 * 4. Lack of Contextual Understanding: Operates at the character level without understanding semantics.
 * 5. Not for Semantic Comparisons: Not ideal for comparing meanings of phrases or sentences.
 * 6. Insensitive to Word Order: Might be misleading where word order impacts meaning.
 * 7. Synonyms/Homonyms: Doesn't account for similar or contextually different meanings.
 **/ 

function distance(str1, str2, threshold) {
    const len1 = str1.length;
    const len2 = str2.length;
    
    if (Math.abs(len1 - len2) > threshold) {
        return threshold + 1; // Return a value greater than the threshold to signify it's above the threshold.
    }

    let prevRow = new Array(len2 + 1).fill(0).map((_, idx) => idx);
    let currRow = new Array(len2 + 1).fill(0);

    for (let i = 1; i <= len1; i++) {
        currRow[0] = i;
        let withinThreshold = false; // This flag will be true if any value in the current row is within the threshold

        for (let j = 1; j <= len2; j++) {
            if (str1[i-1] === str2[j-1]) {
                currRow[j] = prevRow[j-1];
            } else {
                currRow[j] = 1 + Math.min(prevRow[j], currRow[j-1], prevRow[j-1]);
            }

            if (currRow[j] <= threshold) {
                withinThreshold = true;
            }
        }

        if (!withinThreshold) {
            return threshold + 1;
        }

        [prevRow, currRow] = [currRow, prevRow];
    }

    return prevRow[len2];
}

function calculateDistance(str1, str2, threshold = 1000) {
    const memo = {};
    const result = distance(str1, str2, threshold);
    return {
        distance: result,
        table: memo
    };
}

module.exports = calculateDistance;
