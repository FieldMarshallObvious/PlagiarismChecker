import React from 'react';

import styles from './LinkList.module.css';

function LinkList(props) {
    console.log("Props are ", props.data)
  return (
    <div>
      <h2>Similar Links</h2> 
      <div className={styles.similarityList}>
        <ul>
            {props.data.map((item, index) => (
            <li key={index}>
                <a href={item.link} target="_blank" rel="noopener noreferrer">
                {item.title}
                </a>
                <span> - Similarity: {(item.similarity * 100).toFixed(0)}%</span>
            </li>
            ))}
        </ul>
      </div>
    </div>
  );
}

export default LinkList;