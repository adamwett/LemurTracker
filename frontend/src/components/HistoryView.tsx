import { useEffect, useState } from 'react';
import VideoHistory from './VideoHistory';
import DateTimePicker from './DateTimePicker';
import HistoryHeatMap from './HistoryHeatMap';
import { useDateTimeProvider } from '../providers/DateTimeProvider';
import HistoryBarChart from './HistoryBarChart';


const API_BASE_URL = 'http://localhost:5055';

const HistoryView = () => {

    const {dateTime, setDateTime, currentVideoTime, setCurrentVideoTime} = useDateTimeProvider()
    const [activeCamera, setActiveCamera] = useState<number>(0);
    const [activityData, setActivityData] = useState<boolean[]>([])

    const getDateTimeStringToTimestamp = (dateTimeString: string): number => {
        if (!dateTimeString) {
            return 0;
        }
        const date = new Date(dateTimeString);
        if (isNaN(date.getTime())) {
             console.error("Invalid date time string provided:", dateTimeString);
             return 0;
        }
        return date.getTime();
    };

    useEffect(() => {

        const getActivityData = async () => {
            if (!dateTime) {
                console.error("DateTime not set.");
                return;
            }
            if (!dateTime.startTime || !dateTime.endTime) {
                console.error("Start or end datetime not set.");
                return;
            }
        
            const queryParams = new URLSearchParams({
                start_time: dateTime.startTime,
                end_time: dateTime.endTime,
            });
        
            await fetch(`${API_BASE_URL}/activity-data?${queryParams.toString()}`, {
                method: 'GET',
            })
            .then(async (response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const responseData = await response.json();
                setActivityData(responseData.activity);
    
            })
            .then(data => {
                console.log('Activity data received:', data);
            })
            .catch(error => {
                alert('Error fetching activity data, no data in that time range');
    
            });
        }

        getActivityData()
       
    }, [dateTime]);

    return (
        <div className="content-wrapper">
            <div className="left-panel">
                {!dateTime ? 
                    <div>
                        <DateTimePicker setDateTime={setDateTime}/>
                    </div> 
                : 
                    <div>
                        <button 
                            onClick={() => [setDateTime(null), setCurrentVideoTime(0), setActivityData([])]}
                            className="choose-new-date-btn"
                        >
                            Choose new date
                        </button>
                        <VideoHistory videoId={activeCamera} dateTime={dateTime || null} setCurrentTime={setCurrentVideoTime} currentTime={currentVideoTime}/>
                        <div className="camera-buttons">
                            {[0, 1, 2].map((cam) => (
                                <button
                                    key={cam}
                                    className={`cam-button ${activeCamera === cam ? 'active-cam' : 'inactive-cam'}`}
                                    onClick={() => setActiveCamera(cam)}
                                >
                                    Cam {cam + 1}
                                </button>
                            ))}
                        </div>
                        
                    </div>
                }
                
            </div>
            <div className="divider" />
            <div className="right-panel">
                <div style={{height: 350, width: '90%', display: "flex", justifyContent: "center", flexDirection: 'column', alignItems: 'center' }}>
                    <h4>Live Heat Map</h4>
                    <HistoryHeatMap cam={activeCamera}/>
                </div>
                <div style={{height: 350, width: '100%', display: "flex", justifyContent: "center", flexDirection: 'column', alignItems: 'center' }}>
                    <h4>Lemur Activity Over Time</h4>
                    <HistoryBarChart startTime={getDateTimeStringToTimestamp(dateTime?.startTime)} activity={activityData}/>
                </div>
            </div>
        </div>
    );
};

export default HistoryView; 