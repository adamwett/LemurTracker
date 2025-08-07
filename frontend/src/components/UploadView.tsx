import React, { useState } from 'react';
import { useUpdateQueueStatusProvider } from '../providers/UpdateQueueStatus';
import Tooltip from './ToolTip';
declare global {
    interface Window {
        electronAPI: {
            selectFolder: () => Promise<string | null>;
        };
    }
}

const API_BASE_URL = 'http://localhost:5055';

const UploadView: React.FC = () => {
    const [folderPath, setFolderPath] = useState<string | null>(null); 
    const [startDateTimeString, setStartDateTimeString] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null); 
    const { setChange, change } = useUpdateQueueStatusProvider();



    const handleSelectFolderClick = async () => {
        if (!window.electronAPI) {
            console.error("Electron API is not available. Check preload script and contextIsolation settings.");
            setError("Error: Application cannot access folder selection functionality.");
            return;
        }

        setIsLoading(true);
        setError(null);
        setFolderPath(null); 

        try {
            console.log('Requesting folder selection from main process...');
            const selectedPath = await window.electronAPI.selectFolder();

            if (selectedPath) {
                console.log('Folder selected in renderer:', selectedPath);
                setFolderPath(selectedPath);
            } else {
                console.log('Folder selection canceled or no folder selected.');
            }
        } catch (err: any) {
            console.error('Error selecting folder via Electron API:', err);
            setError(`Failed to select folder: ${err.message || 'Unknown error'}`);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDateTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        // The value from datetime-local is already in "YYYY-MM-DDTHH:MM" format
        let newDateTimeString = e.target.value;
        if (newDateTimeString.length === 16) {
            newDateTimeString += ':00';
        }
        console.log('Selected DateTime String:', newDateTimeString);
        setStartDateTimeString(newDateTimeString);
    };



    const handleAddJob = async () => {
        console.log('add-job');
        if (!folderPath || !startDateTimeString) {
            console.error("File path or start date/time not set.");
            // Show error to user
            return;
        }
        const dataToSend = {
            file_path: folderPath,
            start_dt: startDateTimeString,
        };

        await fetch(`${API_BASE_URL}/add-job`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dataToSend),
        }).then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        }).then(data => {
            console.log('Job submission successful:', data);
            alert('Job submitted successfully!');
            setFolderPath(null)
            setStartDateTimeString(null)
            setChange(!change)
            // Handle success (e.g., clear inputs, show message)
        }).catch(error => {
            console.error('Error submitting job:', error);
            setError(`Failed to submit job ${error.message}`);
            // Show error to user
        });
        
    }

    return (
        <div className="content-wrapper">
            <div className="upload-container">
                <h2>Select Video Directory</h2>
                <div className="input-group">
                    <label>Select Folder:</label>
                    <div className="file-input-container">
                        <button
                            className="browse-button"
                            onClick={handleSelectFolderClick}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Selecting...' : 'Browse Folders'}
                        </button>
                    </div>
                </div>
                {folderPath && (
                    <div className="path-display">
                        <h3>Selected Directory (Absolute Path):</h3>
                        <div className="path-text">{folderPath}</div>
                    </div>
                )}
                 {error && (
                    <div className="error-display" style={{ color: 'red', marginTop: '10px' }}>
                        <p>Error: {error}</p>
                    </div>
                )}
                <div className="input-group">
                    <label htmlFor="startDateTime">
                        Start Date & Time: 
                    </label>
                    <input
                        // Change type to datetime-local
                        type="datetime-local"
                        // Update id
                        id="startDateTime"
                        // Bind value to the new state variable
                        value={startDateTimeString}
                        // Use the updated handler
                        onChange={handleDateTimeChange}
                        className="time-input" // Keep or update className as needed
                    />
                    <Tooltip text="Specify when the video footage was recorded." />
                </div>
                <div className="input-group">
                    <label>Select Folder:</label>
                    <div className="file-input-container">
                        <button className="submit-job-button"onClick={handleAddJob} disabled={!startDateTimeString || !folderPath }>
                            Submit Job
                        </button>
                    </div>
                </div>
               
            </div>
            

        </div>
    );
};

export default UploadView;