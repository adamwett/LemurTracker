import { useEffect, useState, useRef } from "react";

type DateTimeDataState = {
    startTime: string;
    endTime: string;
};

type VideoHistoryProps = {
    videoId: number;
    dateTime: DateTimeDataState;
    setCurrentTime: (time: number) => void;
    currentTime: number
};

const API_BASE_URL = 'http://localhost:5055';

const VideoHistory: React.FC<VideoHistoryProps> = ({ videoId, dateTime, setCurrentTime, currentTime }) => {
    const videoRef = useRef<HTMLVideoElement | null>(null);
    const [videoUrl, setVideoUrl] = useState<string>("");

    useEffect(() => {
            if (!dateTime) {
                console.error("DateTime not set.");
                return;
            }
 
            if (!dateTime.startTime && !dateTime.endTime) {
                return;
            }

            const newVideoUrl = `http://localhost:5055/stitched-video?start_time=${
                dateTime.startTime
            }&end_time=${
                dateTime.endTime
            }&camera_name=Camera${videoId + 1}`;

            setVideoUrl(newVideoUrl);

            if (!newVideoUrl) {
                alert("Could not get video");
                return;
            }
            
    }, [dateTime, videoId]);

    const handleTimeUpdate = () => {
        if (videoRef.current && currentTime !==  Math.floor(videoRef.current.currentTime)) {
            setCurrentTime(Math.floor(videoRef.current.currentTime));
        }
    };

    return (
        <div style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: "600px",
            height: "340px",
            backgroundColor: "#1a1a1a",
            borderRadius: "10px",
            boxShadow: "0px 4px 10px rgba(0, 0, 0, 0.5)",
            overflow: "hidden",
            border: "2px solid #333",
            padding: "10px",
        }}>
            {videoUrl && 
            <video
                    ref={videoRef}
                    controls
                    autoPlay
                    muted
                    style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "contain",
                        display: "block",
                    }}
                    
                    src={videoUrl}
                    onTimeUpdate={handleTimeUpdate}
                >
                    Your browser does not support the video tag.
                </video>
            }
        </div>
    );
};

export default VideoHistory;