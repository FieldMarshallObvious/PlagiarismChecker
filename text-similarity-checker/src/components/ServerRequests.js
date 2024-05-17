export const checkSimilarity = (text1, text2, distanceThreshold, searchWeb, algorithim, isHeatMapEnabled, granularity) => {
    // Check if texts are empty or whitespace
    if ( ( !text1.trim() || !text2.trim() ) && ( !searchWeb || algorithim === "LeviathanDistance" ) ) {
        alert("Please enter text in both fields.");
        return;
    } else if( !text1.trim() ) {
        alert("Please enter text!");
        return;
    }

    let bodyRequest = {
        text1: text1,
        text2: text2,
        distanceThreshold: distanceThreshold
    };

    let requestURL = '';

    algorithim = algorithim + (searchWeb ? "Search":"")

    if (isHeatMapEnabled) {
        let pattern;

        if (granularity === "sentences") {
            pattern = "(?<=[.!?])\\s+";
        } else if (granularity === "paragraphs") {
            pattern = "\n";
        }

        bodyRequest.pattern = pattern;
    }

    switch (algorithim) {
        case 'AIModel':
            requestURL = 'http://127.0.0.1:5000/cosine-similarity-model';
            bodyRequest.text = text1;
            bodyRequest.target_texts =  isHeatMapEnabled ? text2.split(bodyRequest.pattern):text2;
            break;
        case 'AIModelSearch':
            requestURL = 'http://127.0.0.1:5000/find_plagiarism';
            bodyRequest.text = text1;
            break;    
        case 'CosineSimilarity':
            requestURL = 'http://127.0.0.1:5000/cosine-similarity';
            bodyRequest.input_texts = [text1];
            bodyRequest.target_texts =  isHeatMapEnabled ? text2.split(bodyRequest.pattern):text2.split("(?<=[.!?])\\s+");
            break;
        case 'CosineSimilaritySearch':
            requestURL = 'http://127.0.0.1:5000/cosine-similarity';
            bodyRequest.input_texts = [text1];
            break;
        case 'LeviathanDistance':
            requestURL = `http://localhost:3001/${isHeatMapEnabled ? "compare-chunks" : "compare"}`;
            break;

        default: 
            requestURL = 'http://127.0.0.1:5000/find_plagiarism';
            bodyRequest.text = text1;

    }


    return fetch(`${requestURL}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(bodyRequest),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Network response was not ok");
        }
        return response.json();
    });
};

export const fetchTable = async ( algorithm ) => {
    let requestURL = '';

    if (algorithm === "LeviathanDistance") 
        requestURL = "http://localhost:3001/chunks"
    else 
        requestURL = "http://127.0.0.1:5000/sentence_similarities"

    const response = await fetch(`${requestURL}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    });

    if (!response.ok) {
        throw new Error("Network response was not ok");
    }

    const data = await response.json();
    let returnData = [];

    console.log("Similarity return data is", data)


    if ( algorithm === "LeviathanDistance" ) {
        returnData = data.chunkSimilarities
    } else  {
       let interpretedData = data.sentence_similarities
       console.log("interpretedData", interpretedData)
       returnData = interpretedData.map(entry => entry.max_similarity * 100);
    }
        

    return returnData;
};

export const fetchYourText = async ( algorithm ) => {
    let requestURL = '';

    if (algorithm === "LeviathanDistance") 
        requestURL = "http://localhost:3001/yourtext"
    else 
        requestURL = "http://127.0.0.1:5000/your_text"


    const response = await fetch(`${requestURL}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
        },
    });

    if (!response.ok) {
        throw new Error("Network response was not ok");
    }

    const data = await response.json();
    let returnData = "";
    if ( algorithm === "LeviathanDistance" ) { returnData = data.yourText }
    else { returnData = data.your_text  }
    return returnData;
};