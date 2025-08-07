import { useState, useEffect } from "react";

// *** ADJUSTED TYPE TO MATCH PYTHON's {x, y} structure ***
// This is the structure we WANT our 'data' state to hold
type ProcessedLemurData = {
    [cameraName: string]: { // e.g., "Camera1"
        coordinates: { x: number; y: number }[]; // Array of {x, y} objects
    };
};

// This type represents the RAW data structure from the Python backend
type BackendResponseData = {
    coordinates: {
        [cameraName: string]: { x: number; y: number }[];
    }[]; // An array of objects, each like { "Camera1": [...] }
};


// Your other types remain the same
type DateTimeDataState = { date: string; startTime: string; endTime: string };
const API_BASE_URL = 'http://localhost:5055';

export const useGetHistory = () => {
    const [dateTime, setDateTime] = useState<DateTimeDataState | null>(null);
    const [currentVideoTime, setCurrentVideoTime] = useState<number>(0);
    // *** State now holds the Processed data structure ***
    const [data, setData] = useState<ProcessedLemurData>({});
    const [filteredData, setFilteredData] = useState<ProcessedLemurData>({}); // Should also use the processed type
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null); // Add error state

    useEffect(() => {
        const fetchLemurTrackingData = async () => {
            if (dateTime?.startTime && dateTime?.endTime) { // Ensure dateTime and times exist
                setLoading(true);
                setError(null); // Reset error on new fetch
                setData({}); // Clear old data immediately
                setFilteredData({});

                try {
                    const queryParams = new URLSearchParams({
                        start_time: dateTime.startTime,
                        end_time: dateTime.endTime,
                    });

                    const response = await fetch(`${API_BASE_URL}/coordinate-data?${queryParams.toString()}`);

                    if (!response.ok) {
                        // Attempt to read error message from backend if available
                        const errorBody = await response.text();
                         throw new Error(`HTTP error! status: ${response.status}. ${errorBody || 'No details.'}`);
                    }

                    const responseData: BackendResponseData = await response.json();
                    console.log('Raw coordinate data received:', responseData);

                    // --- *** TRANSFORMATION STEP *** ---
                    const processedData: ProcessedLemurData = {};
                    if (responseData.coordinates && Array.isArray(responseData.coordinates)) {
                        responseData.coordinates.forEach(cameraObj => {
                            // cameraObj is like { "Camera1": [{x:1,y:1}, ...] }
                            const cameraName = Object.keys(cameraObj)[0]; // Get the camera name (e.g., "Camera1")
                            if (cameraName) {
                                const coordsList = cameraObj[cameraName]; // Get the array [{x:1,y:1}, ...]
                                processedData[cameraName] = { coordinates: coordsList || [] }; // Assign in the desired structure, ensure coordsList is an array
                            }
                        });
                    } else {
                        console.warn("Received data.coordinates is not in the expected array format:", responseData);
                         // You might still want to set data to empty or handle differently
                    }
                    // --- End Transformation ---

                    console.log('Processed coordinate data for state:', processedData);
                    setData(processedData); // Set the correctly structured data

                    // Remove the confusing second .then() chain
                    // .then(data => {
                    //     console.log('Activity data received:', data); // This 'data' was undefined previously
                    // })

                } catch (err) {
                    console.error("Fetch error:", err);
                    setError(err instanceof Error ? err.message : 'An unexpected error occurred');
                    // alert('Error fetching activity data, no data in that time range'); // Use setError instead of alert
                    setData({}); // Clear data on error
                } finally {
                    setLoading(false);
                }
            } else if (dateTime) {
                 // Handle case where dateTime object exists but times are missing
                 console.warn("Start or end datetime not set in dateTime object.");
                 setData({});
                 setFilteredData({});
            }
        };

        fetchLemurTrackingData();
    }, [dateTime]); // Dependency array is correct

    useEffect(() => {
        // Ensure data is not empty and has own properties before proceeding
        if (data && Object.keys(data).length > 0 && currentVideoTime > 0) {
            setLoading(true); // Indicate processing
            try {
                // Now 'data' has the structure: { Camera1: { coordinates: [...] }, ... }
                const newFilteredData: ProcessedLemurData = Object.fromEntries(
                    Object.entries(data).map(([cameraName, cameraData]) => {
                        // Destructure cameraData safely
                        const coordinates = cameraData?.coordinates; // Use optional chaining

                        // Check if coordinates is actually an array before slicing
                        if (Array.isArray(coordinates)) {
                             // Calculate slice end index based on time and assumed frame rate (15 fps?)
                             // Ensure the index is an integer and not out of bounds
                            const endIndex = Math.max(0, Math.min(coordinates.length, Math.floor(currentVideoTime * 15)));
                            return [
                                cameraName,
                                {
                                    coordinates: coordinates.slice(0, endIndex), // Slice the array of {x, y} objects
                                },
                            ];
                        } else {
                            // If coordinates isn't an array for some reason, return empty or handle error
                             console.warn(`Coordinates for camera ${cameraName} is not an array:`, coordinates);
                             return [cameraName, { coordinates: [] }];
                        }
                    })
                );
                // console.log("Filtered data:", newFilteredData);
                setFilteredData(newFilteredData);

            } catch (error) {
                 console.error("Error during data filtering:", error);
                 // Handle filtering error, maybe set filteredData to empty
                 setFilteredData({});
            } finally {
                setLoading(false); // Finish processing
            }

        } else if (currentVideoTime === 0 && Object.keys(data).length > 0) {
             // If video time is reset to 0, clear filtered data
             setFilteredData({});
        }
        // Add basic check to clear filteredData if data itself becomes empty
        else if (!data || Object.keys(data).length === 0) {
            setFilteredData({});
        }

    }, [currentVideoTime, data]); // Dependencies are correct

    // Return the error state as well
    return { dateTime, setDateTime, currentVideoTime, setCurrentVideoTime, filteredData, data, loading, error };
};