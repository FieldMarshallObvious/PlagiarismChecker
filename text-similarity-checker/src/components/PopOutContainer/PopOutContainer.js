import ReactDOM from 'react-dom';
import styles from './PopOutContainer.module.css';

const PopoutContainer = ({ children, isOpen }) => {
    if (!isOpen) return null;

    return ReactDOM.createPortal(
        <div className={`${styles.popoutcontainer} ${isOpen ? styles.open : ''}`}>
            {children}
            {/* Close button or other elements can be added */}
        </div>,
        document.body
    );
};

export default PopoutContainer;