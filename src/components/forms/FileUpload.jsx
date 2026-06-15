import { useRef, useState } from 'react';
import Button from '../common/Button';
import { uploadMockFile } from '../../services/uploadService.js';

function formatBytes(bytes) {
  if (!bytes) return '0 KB';
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileUpload({
  compact = false,
  label = 'Attachment upload',
  onUploaded,
}) {
  const inputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFiles = async (event) => {
    const selectedFiles = Array.from(event.target.files || []);
    if (!selectedFiles.length) return;

    setIsUploading(true);
    const uploads = await Promise.all(selectedFiles.map((file) => uploadMockFile(file)));
    setFiles((current) => [...current, ...uploads]);
    uploads.forEach((attachment) => onUploaded?.(attachment));
    setIsUploading(false);
    event.target.value = '';
  };

  return (
    <div className={`file-upload ${compact ? 'file-upload--compact' : ''}`}>
      <input
        ref={inputRef}
        type="file"
        multiple
        aria-label={label}
        onChange={handleFiles}
      />
      <div className="file-upload__dropzone">
        <span className="file-upload__icon" aria-hidden="true">
          UP
        </span>
        <div>
          <strong>{label}</strong>
          <p>Files are stored in the local mock session only.</p>
        </div>
        <Button
          variant="outline"
          disabled={isUploading}
          onClick={() => inputRef.current?.click()}
        >
          {isUploading ? 'Uploading...' : 'Choose file'}
        </Button>
      </div>
      {files.length > 0 && (
        <ul className="file-upload__list">
          {files.map((file) => (
            <li key={file.id}>
              <span aria-hidden="true">AT</span>
              <div>
                <strong>{file.name}</strong>
                <small>{formatBytes(file.size)}</small>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
