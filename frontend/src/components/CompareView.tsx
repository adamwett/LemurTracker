import CompareSide from "./CompareSide";

const CompareView = () => {
    return (
        <div className="content-wrapper" style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'flex-start',
            gap: '2rem',
            padding: '2rem',
            height: '100%'
        }}>
            <div className="left-panel" style={{ flex: 1, maxWidth: '45%' }}>
                <CompareSide />
            </div>
            <div className="divider" style={{ 
                width: '2px',
                backgroundColor: '#e0e0e0',
                alignSelf: 'stretch'
            }}/>
            <div className="right-panel" style={{ flex: 1, maxWidth: '45%' }}>
                <CompareSide />
            </div>
        </div>
    );
};

export default CompareView;