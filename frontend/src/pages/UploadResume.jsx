import { useState } from "react";
import { api } from "../services/api";

function UploadResume() {

  const [file, setFile] = useState(null);

  const handleUpload = async () => {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(
      "/resume/upload",
      formData
    );

    console.log(response.data);
  };

  return (
    <div>

      <input
        type="file"
        onChange={(e) =>
          setFile(e.target.files[0])
        }
      />

      <button
        onClick={handleUpload}
      >
        Upload Resume
      </button>

    </div>
  );
}

export default UploadResume;