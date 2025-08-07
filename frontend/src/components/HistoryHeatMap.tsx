import { useEffect, useRef, useState } from "react";
import h337 from "heatmap.js";
import { useDateTimeProvider } from "../providers/DateTimeProvider";

const HistoryHeatMap = ({ cam }: { cam: number }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const heatmapContainerRef = useRef<HTMLDivElement>(null);
  const heatmapInstanceRef = useRef<any>(null);
  const [currentImage, setCurrentImage] = useState<string>(`./img/cam_${cam + 1}_image.png`);
  const [containerSize, setContainerSize] = useState({ width: 1, height: 1 });
  const {filteredData} = useDateTimeProvider()

  const coordinates: any[] = filteredData?.[`Camera${cam + 1}`]?.coordinates || [];

  //console.log(test)
  

  useEffect(() => {
    if (containerRef.current) {
      setContainerSize({
        width: containerRef.current.clientWidth,
        height: containerRef.current.clientHeight,
      });
    }
  }, []);

  // Normalize coordinates to fit the container's size
  const normalizedCoordinates = coordinates.map(({x, y}, index) => {
    if (x !== null && y !== null) {
      return {
        x: x * (containerSize.width / 640),
        y: y * (containerSize.height / 480),
        value: 1
      };
    }
    return null;
  }).filter(coord => coord !== null);

  useEffect(() => {
    if (heatmapContainerRef.current && !heatmapInstanceRef.current) {
      heatmapInstanceRef.current = h337.create({
        container: heatmapContainerRef.current,
        radius: 20,
        maxOpacity: 0.6,
        minOpacity: 0.1,
        blur: 0.75,
      });
    }
  }, []);

  useEffect(() => {
    if (heatmapInstanceRef.current) {
      heatmapInstanceRef.current.setData({
        max: 1,
        data: normalizedCoordinates.map((coord: any) => ({
          x: Math.round(coord.x),
          y: Math.round(coord.y),
          value: coord.value,
        })),
      });
    }
  }, [normalizedCoordinates]);

  useEffect(() => {
    setCurrentImage(`./img/cam_${cam + 1}_image.png`);
  }, [cam]);



  return (
    <div
      ref={containerRef}
      style={{
        position: "relative",
        width: "80%",
        height: "80%",
        backgroundColor: "#1a1a1a",
        borderRadius: "10px",
        boxShadow: "1px 10px 10px rgba(0, 0, 0, 0.5)",
        overflow: "hidden",
        border: "2px solid #333",
        padding: "0px",
      }}
    >
      <img
        src={currentImage}
        alt={`Heat_Map_${cam}`}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          position: "absolute",
          zIndex: 0,
        }}
      />
      <div
        ref={heatmapContainerRef}
        style={{ width: "100%", height: "100%", position: "absolute", zIndex: 1 }}
      />
    </div>
  );
};

export default HistoryHeatMap;
