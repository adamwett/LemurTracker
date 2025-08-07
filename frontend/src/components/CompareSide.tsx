import { useState } from "react";
import HistoryBarChart from "./HistoryBarChart";

const API_BASE_URL = 'http://localhost:5055';

const CompareSide = () => {
    const [startDateTimeString, setStartDateTimeString] = useState<string>('');
    const [endDateTimeString, setEndDateTimeString] = useState<string>('');
    const [data, setData] = useState<boolean[]>([]);
    const activity: boolean[] = [
        true, true, false, true, false, true, false, true, false, true,
    ];

    const handleDateTimeChangeStart = (e: React.ChangeEvent<HTMLInputElement>) => {
        // The value from datetime-local is already in "YYYY-MM-DDTHH:MM" format
        let newDateTimeString = e.target.value;
        if (newDateTimeString.length === 16) {
            newDateTimeString += ':00';
        }
        console.log('Selected DateTime String:', newDateTimeString);
        setStartDateTimeString(newDateTimeString);
    };

    const handleDateTimeChangeEnd = (e: React.ChangeEvent<HTMLInputElement>) => {
        // The value from datetime-local is already in "YYYY-MM-DDTHH:MM" format
        let newDateTimeString = e.target.value;
        if (newDateTimeString.length === 16) {
            newDateTimeString += ':00';
        }
        console.log('Selected DateTime String:', newDateTimeString);
        setEndDateTimeString(newDateTimeString);
    };

    const getDateTimeStringToTimestamp = (dateTimeString: string): number => {
        if (!dateTimeString) {
            return 0; // Or perhaps NaN or null depending on how HistoryBarChart handles invalid input
        }
        // The Date constructor can parse ISO 8601 format directly
        const date = new Date(dateTimeString);
        // Check if the date is valid before getting the time
        if (isNaN(date.getTime())) {
             console.error("Invalid date time string provided:", dateTimeString);
             return 0; // Return 0 or handle error appropriately
        }
        return date.getTime(); // Returns milliseconds since epoch
    };

    const handleSubmit = async () => {
        if (!endDateTimeString || !startDateTimeString) {
            console.error("Start or end datetime not set.");
            return;
        }
    
        const queryParams = new URLSearchParams({
            start_time: startDateTimeString,
            end_time: endDateTimeString,
        });
    
        await fetch(`${API_BASE_URL}/activity-data?${queryParams.toString()}`, {
            method: 'GET',
        })
        .then(async (response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const responseData = await response.json();
            setData(responseData.activity);

        })
        .then(data => {
            console.log('Activity data received:', data);
        })
        .catch(error => {
            alert('Error fetching activity data, no data in that time range');

        });
    };
    

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', marginTop: '3rem' }}>
            <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '0.75rem', 
                marginBottom: '0.75rem',
                width: '100%',
                maxWidth: '400px'
                
            }}>
                <div className="date-picker-container" style={{ 
                    display: 'flex', 
                    flexDirection: 'column',
                    gap: '0.1rem', 
                    alignItems: 'center'
                }}>
                    <div className="input-group" style={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        gap: '0.1rem',
                        width: '100%'
                    }}>
                        <h4 style={{ margin: 0, textAlign: 'center' }}>Start Period</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.05rem' }}>
                            <label htmlFor="startDateTime" style={{ textAlign: 'center' }}>Start Date & Time:</label>
                            <input
                                type="datetime-local"
                                id="startDateTime"
                                value={startDateTimeString}
                                onChange={handleDateTimeChangeStart}
                                className="time-input"
                                style={{ width: '100%', padding: '0.35rem' }}
                            />
                        </div>
                    </div>
                    <div className="input-group" style={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        gap: '0.0rem',
                        width: '100%'
                    }}>
                        <h4 style={{ margin: 0, textAlign: 'center' }}>End Period</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.1rem' }}>
                            <label htmlFor="endDateTime" style={{ textAlign: 'center' }}>End Date & Time:</label>
                            <input
                                type="datetime-local"
                                id="endDateTime"
                                value={endDateTimeString}
                                onChange={handleDateTimeChangeEnd}
                                className="time-input"
                                style={{ width: '100%', padding: '0.35rem' }}
                            />
                        </div>
                    </div>
                </div>
                <button 
                    onClick={handleSubmit}
                    disabled={!startDateTimeString || !endDateTimeString}
                    className="submit-job-button"
                >
                    Submit time
                </button>
            </div>
            <div style={{height: 400, width: '100%', display: "flex", justifyContent: "center", flexDirection: 'column', alignItems: 'center', marginTop: '3rem'}}>
                <h4>Lemur Activity Over Time</h4>
                <HistoryBarChart startTime={getDateTimeStringToTimestamp(startDateTimeString)} activity={data}/>
            </div>
        </div>
    )
}


export default CompareSide