"use client"
import React, { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [fileURL, setFileURL] = useState("");
  const [fileName, setFileName] = useState('');

  const uploadFile = async () => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      const fileID = data.id; // Get the file ID from the response
      setFileURL(`http://127.0.0.1:8000/api/files/${fileID}`); // Construct the URL to fetch the PDF
    } catch (error) {
      console.error("Upload failed", error);
    }
  };

  return (
    <div className="flex flex-wrap w-full min-h-screen bg-gray-50">
      <div className="w-full md:w-1/2 xl:w-1/2 p-4">        
        {fileURL && (
          <iframe src={fileURL} style={{width: '100%', height: '700px'}}></iframe>
        )}
      </div>
      <div className="w-full md:w-1/2 xl:w-1/2 flex flex-col items-center justify-center p-4">
        <div className="flex flex-col items-center justify-center bg-white p-6 shadow-lg rounded-lg w-3/4">
          <label htmlFor="file-upload" className="cursor-pointer mb-4 p-2 bg-purple-600 hover:bg-purple-700 focus:ring-4 focus:ring-purple-300 text-white text-sm rounded-lg">
            Choose a file
            <input
              id="file-upload"
              type="file"
              onChange={(e) => {
                const file = e.target.files ? e.target.files[0] : null;
                setFile(file);
                setFileName(file ? file.name : '');
                if (file) {                  
                  const url = URL.createObjectURL(file);
                  setFileURL(url);
                }
              }}
              className="sr-only"
            />
          </label>
          {fileName && (
            <div className="text-sm text-gray-600 mb-4">Selected file: {fileName}</div>
          )}
          <button onClick={uploadFile} className="px-6 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            Upload Document
          </button>
        </div>
      </div>
    </div>
  );
}