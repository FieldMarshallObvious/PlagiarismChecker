import React from 'react';

function Settings( {searchText, setSearch, 
                    algorithim, setAlgorithim,
                    distanceThreshold, setDistanceThreshold, 
                    isHeatmapEnabled, setIsHeatmapEnabled, 
                    granularity, setGranularity} ) {
    return (
        <div className="settings" style={{textAlign: "left"}}>
            {/* Enable Text Search */}
            <div className="setting-item" style={{marginTop: "10px"}}>
                <label htmlFor="searchWebText">Search Text:</label>
                <input 
                    type="checkbox" 
                    id="searchWebText" 
                    checked={searchText} 
                    onChange={(e) => setSearch(e.target.checked)}
                    style={{marginLeft: "10px"}} 
                    disabled={(algorithim === "AIModel" || algorithim === "LeviathanDistance")}
                />
            </div>

            {/* Enable Heatmap */}
            <div className="setting-item" style={{marginTop: "10px"}}>
                <label htmlFor="enableHeatmap">Enable Heatmap:</label>
                <input 
                    type="checkbox" 
                    id="enableHeatmap" 
                    checked={isHeatmapEnabled} 
                    onChange={(e) => {
                        if (algorithim !== "CosineSimilarity") {
                            setIsHeatmapEnabled(e.target.checked);
                        }
                        else 
                            setIsHeatmapEnabled(false);
                    }}
                    disabled={!(algorithim !== "CosineSimilarity")}
                    style={{marginLeft: "10px"}} 
                />
            </div>

            {/* Model Selection */}
            <div className="setting-item" style={{marginTop: "10px"}}>
                <label htmlFor="model">Model:</label>
                <select 
                    id="granularity" 
                    value={algorithim} 
                    onChange={(e) => {
                            setAlgorithim(e.target.value)

                            switch (e.target.value) {
                                case 'AIModel':
                                    setSearch(true)
                                    setIsHeatmapEnabled(false)
                                break

                                case 'CosineSimilarity':
                                    setIsHeatmapEnabled(false)
                                break

                                case 'LeviathanDistance':
                                    setSearch(false)
                                break

                                default:
                                    console.error("No valid option selected!")
                            }

                        }}
                    style={{marginLeft: "10px"}}
                >
                    <option value="AIModel">AI Model</option>
                        <option value="CosineSimilarity">Cosine Similarity</option>
                        {/*//! LeviathanDistance was removed from dropdown */}
                        {/*//! should be added later when the route is fixed */}
                    </select>
            </div>

            {/* Distance Threshold */}
            <div className="setting-item"  style={{marginTop: "10px"}}>
                <label htmlFor="distanceThreshold">Distance Threshold:</label>
                <input 
                        type="number" 
                        id="distanceThreshold" 
                        min="0"
                        value={distanceThreshold} 
                        onChange={(e) => {
                            const value = Math.max(0, Number(e.target.value));
                            setDistanceThreshold(value);
                        }} 
                        style={{marginLeft: "10px"}}
                        disabled={!(algorithim === "LeviathanDistance")}
                    />
            </div>

            {/* Granularity of Search */}
            <div className="setting-item" style={{marginTop: "10px"}}>
                <label htmlFor="granularity">Granularity:</label>
                <select 
                    id="granularity" 
                    value={granularity} 
                    onChange={(e) => setGranularity(e.target.value)}
                    style={{marginLeft: "10px"}}
                    disabled={!isHeatmapEnabled || (algorithim !== "LeviathanDistance")} // Disable if heatmap is not enabled
                >
                    <option value="sentences">Sentences</option>
                    <option value="paragraphs">Paragraphs</option>
                </select>
            </div>
        </div>
    );
}

export default Settings;
