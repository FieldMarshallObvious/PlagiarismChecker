import React, { useState } from 'react';
import { checkSimilarity } from '../ServerRequests';
import LinkList from './../LinkList.js';

import styles from './TextSimilarityChecker.module.css';

function TextSimilarityChecker( {searchText, algorithim, setLastUpdated, isHeatMapEnabled, granularity, distanceThreshold}  ) {
    const [text1, setText1] = useState('');
    const [text2, setText2] = useState('');
    const [similarity, setSimilarity] = useState(null);
    const [links, setLinks] = useState('')
    const [isLoading, setIsLoading] = useState(false);
    const [delayHandler, setDelayHandler] = useState(null);



    const handleCheckSimilarity = () => {
        setLinks('')
        
        const handler = setTimeout(() => {
            setIsLoading(true);
        }, 100)

        setDelayHandler(handler);

        checkSimilarity(text1, text2, distanceThreshold, searchText, algorithim, isHeatMapEnabled, granularity)
        .then(data => {
            clearTimeout(delayHandler);
            console.log("Response is", data)
            console.log("Data similarity is", data.similarity * 100);
            setLastUpdated(Date.now());
            setSimilarity(Math.round(data.similarity * 100));
            setLinks(data.SortedUrls)
            setIsLoading(false);
        })
        .catch(error => {
            clearTimeout(delayHandler);
            console.error("There was a problem with the fetch operation:", error);
            alert("There was an error processing your request. Please try again later.");
            setIsLoading(false);
        });
    };
    

    return (
        <div className={styles.TextSimilarityContainer}>
            <h1 className="mb-4" style={{textAlign: "start", fontWeight: "bold", fontSize: "32px"}}>Plagiarism Checker</h1>

            <div className="row">
                <div className={`col-${searchText && links.length === 0 ? 'md-12' : 'md-6'} col-12 mb-3`}>            
                    <label htmlFor="text1" className={styles.boxTitle}>Your Text</label>
                    <textarea 
                        className={"form-control " + styles.TextFormContainer} 
                        id="text1" 
                        value={text1} 
                        onChange={(e) => setText1(e.target.value)} 
                        placeholder="Enter/Paste your text here" 
                        rows="4"
                    ></textarea>
                </div>

                {!searchText && (
                    <div className="col-md-6 col-12 mb-3">
                        <label htmlFor="text2" className={styles.boxTitle}>Source Text</label>
                        <textarea 
                            className={`form-control ${styles.TextFormContainer}`} 
                            id="text2" 
                            value={text2} 
                            onChange={(e) => setText2(e.target.value)} 
                            placeholder="Enter/Paste Source text here" 
                            rows="4"
                        ></textarea>
                    </div>
                )}
                {(links && searchText) && (
                    <div className="col-md-6 col-12 mb-3">
                        <LinkList data={links} />
                    </div>
                )}
            </div>
            



            <div className="mt-3">
                <button className={"btn btn-primary " + styles.CheckButton} onClick={handleCheckSimilarity}>Check Similarity</button>
            </div>

            <div style={{textAlign: 'center', paddingTop: "18px"}}>
                <div className="progress" style={{maxWidth: "806px", height:"43px",margin: '0 auto'}}>
                    <div className="progress-bar bg-danger" role="progressbar" style={{width: `${similarity}%`}} aria-valuenow="100" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </div>
            



            <span  className={"mt-4 " + styles.percentAmount}>Similarity Score:</span>
            { !isLoading && (<span className={styles.EmphasizeRed}>{similarity !== null ? `${similarity}%` : 'N/A'}</span>)}
            { isLoading && (<span className={styles.EmphasizeRed + ' ' + styles.EmphasizeRedAnimated}>Loading</span>)}
        </div>
    );
}

export default TextSimilarityChecker;
