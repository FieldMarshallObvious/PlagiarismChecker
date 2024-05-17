const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const calculatePercentage = require('./CalculatePercent');
const app = express();
const PORT = 3001; 
let distanceTable = [];
let yourText = "";
let chunkSimilarities = [];

app.use(cors());
app.use(bodyParser.json());

app.get('/', (req, res) => {
    res.send('Server is running');
});

app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});

app.post('/compare', (req, res) => {
    const { text1, text2, distanceThreshold } = req.body;

    if (!text1 || !text2) {
        res.status(400).json({ error: 'Both texts are required' });
        return;
    }
    yourText = text1;

    let similarity = calculatePercentage.calculatePercentage(text1, text2, distanceThreshold);

    res.json({ similarity });
});

app.post('/compare-chunks', (req, res) => {
    const { text1, text2, pattern, distanceThreshold } = req.body;
    if (!text1 || !text2) {
        res.status(400).json({ error: 'Both texts are required' });
        return;
    }

    yourText = text1;

    let { newChunkSimilarities, overallSimilarity } = calculatePercentage.calculatePercentageChunks(text1, text2, pattern, distanceThreshold)

    chunkSimilarities = newChunkSimilarities;

    res.json({ chunkSimilarities: chunkSimilarities, similarity: overallSimilarity });
});


app.get('/distances', (req, res) => {
    res.json({distanceTable});
});

app.get('/chunks', (req, res) => {
    res.json({chunkSimilarities});
})

app.get('/yourtext', (req, res) => {
    res.json({yourText});
})