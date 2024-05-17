import React, { useState } from 'react';
import './App.css';
import TextSimilarityChecker from './components/TextSimilarityChecker/TextSimilarityChecker';
import GradientHighlightedText from './components/GradientHighlightedText';
import Settings from './components/Settings';
import fireIcon from './Images/fire.svg';
import settingsIcon from './Images/settings.svg';

function App() {
    let [isPopoutVisible, setPopoutVisible] = useState(false);
    let [isSettingsVisible, setSettingsVisible] = useState(false);
    let [lastUpdated, setLastUpdated] = useState(Date.now());

    const [searchText, setSearch] = useState(true);
    const [distanceThreshold, setDistanceThreshold] = useState(1000);
    const [isHeatmapEnabled, setIsHeatmapEnabled] = useState(false);
    const [algorithim, setAlgorithim] = useState('AIModel');
    const [granularity, setGranularity] = useState('sentences');

    return (
        <div className="App">
            <div className='row' style={{position: "fixed",top: "15px", right: '15px', justifyContent: 'right'}}>
                <img src={fireIcon} alt={"Heatmap Icon"} className='NavIcon' onClick={() => setPopoutVisible(true)} />
                <img src={settingsIcon} alt={"Settings Icon"} className='NavIcon' onClick={() => setSettingsVisible(true)} />
            </div>
            <div className='container-fluid mt-5'>
                <div className={`col-12`}>
                    <TextSimilarityChecker searchText={searchText} algorithim={algorithim} setLastUpdated={setLastUpdated} isHeatMapEnabled={isHeatmapEnabled} granularity={granularity} distanceThreshold={distanceThreshold}/>
                    {/* Heatmap content */}
                    <div className={`col-${isPopoutVisible ? '4' : '0'} offcanvas-col`}>
                    <div className={`offcanvas offcanvas-end ${isPopoutVisible ? 'show' : ''}`} tabIndex="-1" id="offcanvasExample">
                        <div className="offcanvas-header">
                            <h5 className="offcanvas-title">Plaigerism HeatMap</h5>
                            <button type="button" className="btn-close" data-bs-dismiss="offcanvas" aria-label="Close" onClick={() => setPopoutVisible(false)}></button>
                        </div>
                        <div className="offcanvas-body">
                            {isHeatmapEnabled ? 
                            <GradientHighlightedText lastUpdated={lastUpdated} granularity={granularity} algorithm={algorithim}/> : 
                            <div>
                                <h1>HeatMap is not enabled!</h1>
                                <span>Please enable it in </span>
                                <span className="hyperlinktext" onClick={() => {setPopoutVisible(false); setSettingsVisible(true)}}>Settings</span>
                            </div>
                            }
                        </div>
                    </div>
                </div>
                {/* Settings Content */}
                <div className={`col-${isSettingsVisible ? '4' : '0'} offcanvas-col`}>
                    <div className={`offcanvas offcanvas-end ${isSettingsVisible ? 'show' : ''}`} tabIndex="-1" id="offcanvasExample">
                        <div className="offcanvas-header">
                            <h5 className="offcanvas-title">Settings</h5>
                            <button type="button" className="btn-close" data-bs-dismiss="offcanvas" aria-label="Close" onClick={() => setSettingsVisible(false)}></button>
                        </div>
                        <div className="offcanvas-body">
                            <Settings searchText={searchText} setSearch={setSearch} 
                                    algorithim={algorithim} setAlgorithim={setAlgorithim}
                                    distanceThreshold={distanceThreshold} setDistanceThreshold={setDistanceThreshold} 
                                    isHeatmapEnabled={isHeatmapEnabled} setIsHeatmapEnabled={setIsHeatmapEnabled} 
                                    granularity={granularity} setGranularity={setGranularity}
                                    isSettingsVisible={isSettingsVisible} />
                        </div>
                    </div>
                </div>
                </div>
            </div>
   
     </div>
    );
}

export default App;
