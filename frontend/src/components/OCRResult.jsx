import React, { useState, useEffect } from "react";
import { parsePartNumbersFromText } from "../utils/parsePartNumbersFromText";
import "./OCRResult.css";

const OCRResult = ({ ocrText }) => {
    const [partNumbers, setPartNumbers] = useState([]);
    const [selectedPart, setSelectedPart] = useState(null);
    const [partInfo, setPartInfo] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (ocrText) {
            const extracted = parsePartNumbersFromText(ocrText);
            setPartNumbers(extracted);
            setSelectedPart(null);
            setPartInfo(null);
        }
    }, [ocrText]);

    const handleClick = async (part) => {
        setSelectedPart(part);
        setLoading(true);
        setPartInfo(null);

        try {
            const res = await fetch(`/partinfo/?part_number=${encodeURIComponent(part)}`);
            if (!res.ok) throw new Error("Failed to fetch part info");
            const data = await res.json();
            setPartInfo(data);
        } catch (err) {
            console.error("Error fetching part info:", err);
            setPartInfo({ error: "Could not fetch part info." });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ marginTop: "2rem" }}>
            <h2>OCR Text:</h2>
            <pre>{ocrText}</pre>

            {partNumbers.length > 0 && (
                <>
                    <h3>🔎 Detected Part Numbers:</h3>
                    <ul className="part-number-list">
                        {partNumbers.map((pn, idx) => (
                            <li
                                key={idx}
                                className={`part-number-item ${selectedPart === pn ? "selected" : ""
                                    }`}
                                onClick={() => handleClick(pn)}
                            >
                                {pn}
                            </li>
                        ))}
                    </ul>
                </>
            )}

            {loading && <p>🔄 Loading part info...</p>}

            {partInfo && (
                <div className="part-info-box">
                    {partInfo.error ? (
                        <p style={{ color: "red" }}>{partInfo.error}</p>
                    ) : (
                        <>
                            <h4>📦 Part Info for <code>{selectedPart}</code>:</h4>
                            <p><strong>Manufacturer:</strong> {partInfo.manufacturer}</p>
                            <p><strong>Location:</strong> {partInfo.location}</p>
                            <p><strong>Compatible Cars:</strong></p>
                            <ul>
                                {partInfo.compatibleCars?.map((car, idx) => (
                                    <li key={idx}>{car}</li>
                                ))}
                            </ul>
                        </>
                    )}
                </div>
            )}
        </div>
    );
};

export default OCRResult;
