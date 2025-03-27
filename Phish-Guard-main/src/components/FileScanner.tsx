import React, { useState } from 'react';
import { Upload, AlertTriangle, CheckCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';

export function FileScanner() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState<{
    safe: boolean;
    message: string;
  } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setUrl('');
      setResult(null);
    }
  };

  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUrl(e.target.value);
    setFile(null);
    setResult(null);
  };

  const scanContent = async () => {
    setScanning(true);
    try {
      let scanResult;
      
      if (file) {
        // Simulate file scanning (in production, you'd send this to your scanning service)
        const fileType = file.type;
        const isSafe = !file.name.includes('malicious'); // Simple demo check
        
        scanResult = {
          safe: isSafe,
          message: isSafe 
            ? `File appears to be safe. Type: ${fileType}`
            : 'Potential security risk detected in file'
        };

        // Store scan result in Supabase
        const { error } = await supabase
          .from('scans')
          .insert({
            url: file.name,
            severity: isSafe ? 'low' : 'high',
            user_id: (await supabase.auth.getUser()).data.user?.id
          });

        if (error) throw error;
      } else if (url) {
        // Simulate URL scanning
        const isSafe = !url.includes('suspicious') && !url.includes('phishing');
        
        scanResult = {
          safe: isSafe,
          message: isSafe 
            ? 'URL appears to be safe'
            : 'Potential phishing attempt detected'
        };

        // Store scan result
        const { error } = await supabase
          .from('scans')
          .insert({
            url: url,
            severity: isSafe ? 'low' : 'high',
            user_id: (await supabase.auth.getUser()).data.user?.id
          });

        if (error) throw error;
      }

      setResult(scanResult || { safe: false, message: 'Please provide a file or URL to scan' });
    } catch (error) {
      console.error('Scan error:', error);
      setResult({
        safe: false,
        message: 'Error during scan. Please try again.'
      });
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Scan for Threats</h2>
      
      {/* File Upload */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload File (PDF, Images, Documents)
        </label>
        <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
          <div className="space-y-1 text-center">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <div className="flex text-sm text-gray-600">
              <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                <span>Upload a file</span>
                <input
                  type="file"
                  className="sr-only"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx,.txt,image/*"
                />
              </label>
            </div>
            <p className="text-xs text-gray-500">
              PDF, DOC, Images up to 10MB
            </p>
          </div>
        </div>
      </div>

      {/* URL Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Or Enter URL/Email
        </label>
        <input
          type="text"
          className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
          placeholder="https://example.com or email content"
          value={url}
          onChange={handleUrlChange}
        />
      </div>

      {/* Scan Button */}
      <button
        onClick={scanContent}
        disabled={scanning || (!file && !url)}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
      >
        {scanning ? 'Scanning...' : 'Scan Now'}
      </button>

      {/* Results */}
      {result && (
        <div className={`mt-4 p-4 rounded-md ${result.safe ? 'bg-green-50' : 'bg-red-50'}`}>
          <div className="flex">
            <div className="flex-shrink-0">
              {result.safe ? (
                <CheckCircle className="h-5 w-5 text-green-400" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-red-400" />
              )}
            </div>
            <div className="ml-3">
              <h3 className={`text-sm font-medium ${result.safe ? 'text-green-800' : 'text-red-800'}`}>
                {result.safe ? 'Safe Content' : 'Warning'}
              </h3>
              <div className={`mt-2 text-sm ${result.safe ? 'text-green-700' : 'text-red-700'}`}>
                <p>{result.message}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}