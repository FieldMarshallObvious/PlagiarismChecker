import { useState, useEffect } from 'react';
import { fetchTable, fetchYourText } from './ServerRequests.js';



function tableTo2DArray(rawData) {
    const matrix = [];

    for (const key in rawData) {
        if (rawData.hasOwnProperty(key)) {
            let [x, y] = key.split(",").map(Number);
            x--;  // adjust for 0-based index
            y--;  // adjust for 0-based index
            
            if (!matrix[x]) {
                matrix[x] = [];
            }
            
            matrix[x][y] = rawData[key];
        }
    }

    return matrix;
}

function computeColumnAverages(matrix) {
    const colLength = matrix.reduce((max, row) => Math.max(max, row.length), 0);
    const averages = Array(colLength).fill(0);

    for (let j = 0; j < colLength; j++) {
        let sum = 0;
        let count = 0;
        for (let i = 0; i < matrix.length; i++) {
            if (matrix[i][j] !== undefined) {
                sum += matrix[i][j];
                count++;
            }
        }
        averages[j] = sum / count;
    }

    return averages;
}



function mapValueToGradient(value, min, max) {
    const ratio = (value - min) / (max - min);
    
    const red = 255; // Red channel remains constant at 255
    const green = Math.floor(255 * (1 - ratio)); // Decreasing the green channel from 255 to 0
    const blue = Math.floor(255 * (1 - ratio)); // Decreasing the blue channel from 255 to 0
    
    return `rgb(${red}, ${green}, ${blue})`;
}

function GradientHighlightedText({ lastUpdated, activeMap, algorithm, granularity }) {
    const [table, setTable] = useState(null);
    const [yourText, setYourText] = useState(null);

    useEffect(() => {
        if (!lastUpdated) return;
    
        console.log("Using effect");
    
        const getData = async () => {
            try {
                const tableData = await fetchTable(algorithm);
                console.log("Distance table is ", tableData);
                setTable(tableData);
    
                const textData = await fetchYourText(algorithm);
                console.log("Your text is ", textData);
                setYourText(textData);
    
            } catch (error) {
                console.error("There was a problem with the fetch operation:", error);
                alert("There was an error processing your request. Please try again later.");
            }
        };
    
        getData();
    
        // Cleanup to avoid updating state of unmounted components
        return () => {
            setTable(null);
            setYourText(null);
        };
    }, [lastUpdated, algorithm]);    
    
    if (!table || !yourText) return null; // Don't render anything if table is null
    
    //const averages = computeColumnAverages(table);
    const minValue = 0;
    const maxValue = 100;

    let pattern;
        
    if(granularity === "sentences") {
        pattern = /(?<=[.!?])\s+/;
    } 
    else if(granularity === "paragraphs") {
        pattern = "\n";
    }
    
    return (
        <span>
        {yourText.split(pattern).filter(chunk => chunk.trim() !== '').map((char, index) => {
            const value = table[index] || 0; // If the index is out of bounds, default to 0
            const color = mapValueToGradient(value, minValue, maxValue);
            return (
                <div key={index} style={{ backgroundColor: color, textAlign: 'left'}}>
                    {char}
                </div>
            );
        })}
    </span>
    );
}

export default GradientHighlightedText;