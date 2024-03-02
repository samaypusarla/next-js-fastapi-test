import React, { useState } from 'react';
import './DocumentUploader.css';

const DocumentUploader = () => {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(''); 
  const [pdfUrl, setPdfUrl] = useState(''); 

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setPdfUrl('');
  };

  const handleUpload = () => {
    if (!file) {
        alert('Please select a file.');
        return;
    }

    const ws = new WebSocket('ws://127.0.0.1:8000/upload-doc');
    ws.onopen = () => {
        ws.send('start_upload');
        setUploadStatus('Upload started. Uploading file...');
        const reader = new FileReader();
        reader.onload = () => {
            ws.send(reader.result);
        };
        reader.readAsArrayBuffer(file);
    };

    ws.onmessage = (event) => {
        const message = event.data;        
        if (message.startsWith('File saved as: ')) {
            const fileUrl = message.replace('File saved as: ', '');
            setPdfUrl(fileUrl);
            console.log("here is the pdf:", fileUrl)
            setUploadStatus('File uploaded successfully.');
        } else {
            setUploadStatus(message);
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setUploadStatus('Error occurred during upload.');
    };
};

  return (
    <div className="document-uploader-container">
      <div className="document-uploader">
        <h2 className="document-uploader-heading">Upload Your Document</h2>
        <div className="upload-input-container">
          <input type="file" onChange={handleFileChange} className="document-uploader-input" />
          <button onClick={handleUpload} className="document-uploader-button">Upload</button>
        </div>
        {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
      </div>      
      {pdfUrl && (
      <iframe 
        src={pdfUrl} 
        style={{ width: '800px', height: '100%', border: '1px solid #ccc' }}
        title="PDF viewer">
      </iframe>
    )}
    </div>
  );
};

export default DocumentUploader;
