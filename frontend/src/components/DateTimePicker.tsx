import { useState } from "react";

type DateTimeDataState = {
    startTime: string;
    endTime: string;
  };

type DateTimePickerProps = {
    setDateTime: (dateTime: DateTimeDataState) => void;
};

const DateTimePicker: React.FC<DateTimePickerProps> = ({ setDateTime }) => {
    const [startDateTimeString, setStartDateTimeString] = useState<string>('');
    const [endDateTimeString, setEndDateTimeString] = useState<string>('');

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

    const handleSubmit = async () => {
        if (!endDateTimeString || !startDateTimeString) {
            return
        }

        const dateTime: DateTimeDataState = {
            startTime: startDateTimeString,
            endTime: endDateTimeString,
        };
        setDateTime(dateTime);
    }

    return (
        <div style={{ maxWidth: "400px", margin: "20px auto", padding: "20px", border: "1px solid #ccc", borderRadius: "8px", boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.1)", backgroundColor: "#fff" }}>
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
        </div>
    );
    };

    export default DateTimePicker;
