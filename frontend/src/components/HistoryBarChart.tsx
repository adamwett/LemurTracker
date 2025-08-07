import React, { useState, useEffect, useMemo, useCallback } from "react";
import { BarChart, Bar, Rectangle, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface ChartDataPoint {
    name: string;      
    intervalStartMillis: number; 
    intervalEndMillis: number;  
    active: number;        
    inactive: number;
    intervalSize: number; 
}
interface HistoryBarChartProps {
    startTime: number;
    activity: boolean[];
}

const HistoryBarChart = ({ startTime, activity}: HistoryBarChartProps) => {

    const firstTimestamp: number = startTime
    // State for the processed data displayed in the chart
    const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

    // --- Dynamic Interval Calculation (Unchanged) ---
    const getIntervalSize = useCallback((totalSeconds: number): number => {
        if (totalSeconds <= 60) return 10;
        if (totalSeconds <= 300) return 30;
        if (totalSeconds <= 1800) return 60;
        return 300;
    }, []);

    // --- Aggregate Data based on Dynamic Intervals AND Timestamps ---
    const aggregatedData = useMemo(() => {
        const totalSeconds = activity.length;
        // Need the first timestamp to calculate actual interval times
        if (totalSeconds === 0 || firstTimestamp === null) {
            return [];
        }

        const intervalSizeSecs = getIntervalSize(totalSeconds);
        const aggregated: ChartDataPoint[] = [];
        let currentIntervalStartIdx = 0; // Index in activityHistory array

        while (currentIntervalStartIdx < totalSeconds) {
            const currentIntervalEndIdx = Math.min(currentIntervalStartIdx + intervalSizeSecs, totalSeconds);
            let activeCount = 0;
            let inactiveCount = 0;

            // Count within the current interval slice
            for (let i = currentIntervalStartIdx; i < currentIntervalEndIdx; i++) {
                if (activity[i] === true) activeCount++;
                else inactiveCount++;
            }

            // Calculate actual times for the label
            const intervalStartMillis = firstTimestamp + (currentIntervalStartIdx * 1000);
            const intervalEndMillis = firstTimestamp + (currentIntervalEndIdx * 1000);
            const actualIntervalSize = currentIntervalEndIdx - currentIntervalStartIdx; // Size in seconds

            // Format the time label (e.g., HH:MM:SS)
            const formatTime = (millis: number) => new Date(millis).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            const name = `${formatTime(intervalStartMillis)} - ${formatTime(intervalEndMillis)}`;

            aggregated.push({
                name: name, // Use formatted time range
                intervalStartMillis: intervalStartMillis,
                intervalEndMillis: intervalEndMillis,
                active: activeCount,
                inactive: inactiveCount,
                intervalSize: actualIntervalSize,
            });

            currentIntervalStartIdx += intervalSizeSecs; // Move index by interval size
        }
        return aggregated;

    }, [activity, firstTimestamp, getIntervalSize]); // Dependencies

    // --- Update Chart Data State ---
    useEffect(() => {
        setChartData(aggregatedData);
    }, [aggregatedData]);

    // --- Determine Max Y-Axis Value (Unchanged) ---
    const maxYValue = useMemo(() => {
        if (chartData.length === 0) return 10;
        return Math.max(...chartData.map(d => d.intervalSize), 10);
    }, [chartData]);

    // --- Custom Tooltip (Updated to show actual times maybe) ---
    const CustomTooltip = ({ active, payload, label }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload as ChartDataPoint;
            // const startTimeStr = new Date(data.intervalStartMillis).toLocaleTimeString();
            // const endTimeStr = new Date(data.intervalEndMillis).toLocaleTimeString();
            return (
                <div className="custom-tooltip" style={{ /* ... styles ... */ }}>
                    <p className="label" style={{ fontWeight: 'bold', margin: 0 }}>{`${data.name}`}</p> {/* Use formatted name */}
                    <p style={{ margin: '4px 0 0 0', color: '#4CAF50' }}>{`Active: ${data.active}s`}</p>
                    <p style={{ margin: '4px 0 0 0', color: '#F44336' }}>{`Inactive: ${data.inactive}s`}</p>
                    <p style={{ margin: '4px 0 0 0', fontSize: '0.8em', color: '#555' }}>{`(Interval: ${data.intervalSize}s)`}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div style={{ width: "90%", height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
                <BarChart
                    data={chartData}
                    margin={{ top: 5, right: 5, left: 0, bottom: 35 }} // Increased bottom margin for labels
                    barCategoryGap={1}
                >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis
                        dataKey="name" // Now shows HH:MM:SS - HH:MM:SS
                        angle={-30} // Might need more angle or fewer ticks if too long
                        textAnchor="end"
                        height={70} // Increased height
                        interval="preserveStartEnd" // Adjust interval as needed
                        tick={{ fontSize: 9 }} // Slightly smaller font maybe
                    />
                    <YAxis
                        label={{ value: 'Seconds Active', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' }, dy: 40 }}
                        domain={[0, maxYValue]}
                        allowDecimals={false}
                    />
                    <Tooltip content={<CustomTooltip />} />
                    <Legend verticalAlign="top" height={36}/>
                    <Bar dataKey="active" name="Seconds Active" fill="#4CAF50" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default HistoryBarChart;