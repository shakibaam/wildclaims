import pandas as pd
import json
import os
from openai import OpenAI


def submit_openai_batch(jsonl_path: str, metadata_path: str, description: str = "batch run", completion_window: str = "24h") -> dict:
    """
    Submits a batch job to OpenAI and saves metadata for later retrieval.

    Args:
        jsonl_path (str): Path to the JSONL file containing requests.
        metadata_path (str): Where to save the metadata JSON.
        description (str): Description for the batch job.
        completion_window (str): Completion window for the batch job.

    Returns:
        dict: Metadata including batch ID and input file ID.
    """
    openai_client = OpenAI()
    with open(jsonl_path, "rb") as f:
        input_file = openai_client.files.create(file=f, purpose="batch")
    print(f"✅ Uploaded file: {input_file.id}")
    batch = openai_client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window=completion_window,
        metadata={"description": description}
    )
    print(f"🚀 Batch submitted: {batch.id}")
    metadata = {
        "batch_id": batch.id,
        "input_file_id": input_file.id
    }
    with open(metadata_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(metadata, ensure_ascii=False) + "\n")
    return metadata


def get_batch_statuses_from_metadata(metadata_jsonl_path: str) -> list:
    """
    Retrieves the status of all batches listed in a metadata JSONL file.

    Args:
        metadata_jsonl_path (str): Path to the metadata JSONL file.

    Returns:
        list: List of dicts with batch_id and status.
    """
    client = OpenAI()
    statuses = []
    with open(metadata_jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                batch_id = data.get('batch_id')
                if batch_id:
                    response = client.batches.retrieve(batch_id)
                    print(response)
                    statuses.append({'batch_id': batch_id, 'status': response.status})
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line: {line}")
    return statuses


def fetch_batch_output(metadata_path: str, save_path: str):
    """
    Fetches and saves the completed batch output file.

    Args:
        metadata_path (str): Path to saved batch metadata (JSON file).
        save_path (str): File path to save the output.
    """
    openai_client = OpenAI()
    with open(metadata_path, "r") as meta_f:
        metadata = json.load(meta_f)
    batch_id = metadata["batch_id"]
    batch = openai_client.batches.retrieve(batch_id)
    print(f"📦 Batch status: {batch.status}")
    if batch.status != "completed":
        print("⏳ Batch is not completed yet.")
        return
    output_file_id = batch.output_file_id
    metadata["output_file_id"] = output_file_id
    file_content = openai_client.files.content(output_file_id)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(file_content.text)
    print(f"✅ Output file saved to {save_path}")
    with open(metadata_path, "w") as meta_f:
        json.dump(metadata, meta_f, indent=2)


def split_jsonl_file(input_jsonl_path, output_dir, lines_per_file=10000):
    """
    Splits a large JSONL file into smaller chunks.
    Args:
        input_jsonl_path (str): Path to the input JSONL file.
        output_dir (str): Directory to save the split files.
        lines_per_file (int): Number of lines per split file.
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    with open(input_jsonl_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    total_lines = len(lines)
    num_files = (total_lines + lines_per_file - 1) // lines_per_file  # Ceiling division
    for i in range(num_files):
        start_idx = i * lines_per_file
        end_idx = min((i + 1) * lines_per_file, total_lines)
        output_file = os.path.join(output_dir, f"batch_requests_part_{i+1:02d}.jsonl")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(lines[start_idx:end_idx])
        print(f"Created {output_file} with {end_idx - start_idx} lines") 