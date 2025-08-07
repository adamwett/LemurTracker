import React, { useState, useEffect } from 'react';
import type {
    QueueStatusResponse,
    QueueComponentState,
} from '../types/queue';
import { useUpdateQueueStatusProvider } from '../providers/UpdateQueueStatus';

// --- Component ---
const QueueStatusDisplay: React.FC = () => {
    const [queueState, setQueueState] = useState<QueueComponentState>({
        isLoading: true,
        error: null,
        data: null,
    });

    const API_ENDPOINT = 'http://localhost:5055/get-queue-status';
    const POLLING_INTERVAL = 10000;
    const { change } = useUpdateQueueStatusProvider();

    const fetchQueueStatus = async () => {
        try {
            const response = await fetch(API_ENDPOINT);

            if (!response.ok) {
                let errorMsg = `HTTP error ${response.status}: ${response.statusText}`;
                try {
                    const errorData = await response.json();
                    if (errorData && errorData.error) {
                        errorMsg = errorData.error;
                    }
                } catch (jsonError) {
                }
                 throw new Error(errorMsg);
            }

            const data: QueueStatusResponse = await response.json();

            setQueueState({
                isLoading: false,
                error: null,
                data: data,
            });

        } catch (error) {
            console.error("Failed to fetch queue status:", error);
            const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
            setQueueState(prev => ({
                ...prev,
                isLoading: false,
                error: errorMessage,
            }));
        }
    };

    useEffect(() => {
        fetchQueueStatus();
        const intervalId = setInterval(fetchQueueStatus, POLLING_INTERVAL);
        return () => {
            clearInterval(intervalId);
        };
    }, []);

    useEffect(() => {
        fetchQueueStatus();
    }, [change]);

    if (queueState.isLoading && !queueState.data) {
        return <div>Loading queue status...</div>;
    }

    if (queueState.error) {
        return <div style={{ color: 'red' }}>Error fetching queue status: {queueState.error}</div>;
    }

    if (queueState.data?.status === 'not processing') {
        return <div>There are no videos currently processing.</div>;
    }

    if (queueState.data?.status === 'processing') {
        const { current_process, processes_on_deck } = queueState.data;

        return (
            <div style={styles.container}>
                <h2>Currently Processing</h2>
                <p style={styles.filePath}>{current_process.file_path}</p>

                <div style={styles.progressBarContainer}>
                    <div
                        style={{
                            ...styles.progressBarFill,
                            width: `${current_process.percent}%`, 
                        }}
                    >
                        {current_process.percent}%
                    </div>
                </div>

                {processes_on_deck.length > 0 && (
                    <div style={styles.onDeckContainer}>
                        <h3>On Deck</h3>
                        <ul style={styles.list}>
                            {processes_on_deck.map((filePath, index) => (
                                <li key={`${filePath}-${index}`} style={styles.listItem}> 
                                    {filePath}
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
                 {processes_on_deck.length === 0 && (
                     <p>No other items waiting in the queue.</p>
                 )}

                 {queueState.isLoading && <div style={styles.subtleLoading}>Updating...</div>}
            </div>
        );
    }

    return  <div>Waiting for queue status...</div>;
};


const styles: { [key: string]: React.CSSProperties } = {
    container: {
        fontFamily: 'sans-serif',
        padding: '20px',
        border: '1px solid #ccc',
        borderRadius: '8px',
        maxWidth: '600px',
    },
    filePath: {
        wordBreak: 'break-all',
        marginBottom: '15px',
    },
    progressBarContainer: {
        width: '100%',
        backgroundColor: '#e0e0e0',
        borderRadius: '4px',
        height: '25px',
        marginBottom: '20px',
        overflow: 'hidden',
    },
    progressBarFill: {
        height: '100%',
        backgroundColor: '#4caf50',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '0.8em',
        borderRadius: '4px',
        transition: 'width 0.3s ease-in-out',
    },
    onDeckContainer: {
        marginTop: '20px',
        borderTop: '1px dashed #eee',
        paddingTop: '15px',
    },
    list: {
        listStyle: 'none',
        paddingLeft: '0',
    },
    listItem: {
        backgroundColor: '#f9f9f9',
        padding: '5px 10px',
        marginBottom: '5px',
        borderRadius: '3px',
        fontSize: '0.9em',
        wordBreak: 'break-all',
    },
    subtleLoading: {
        fontSize: '0.8em',
        color: '#888',
        marginTop: '10px',
        textAlign: 'right',
    }
};


export default QueueStatusDisplay;