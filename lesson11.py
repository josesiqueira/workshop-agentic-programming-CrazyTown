r"""
Lesson 11: Pydantic AI agent framework - Extracting structured information from an image, in an agentic way with watch folder
Not using database, just a CSV file, it is appending at the end of the file, every time a new image is processed.

Is this already an AI agent? 

This is NOT an AI agent. An agent would have:
- Temporal continuity (a loop running over time)
- Tools/actuators (search, database, filesystem, etc.)
- State/memory across steps
- Goal-directed behavior

We will see that in the next lesson.

Setup:

Always create a virtual environment
1. python -m venv venv
2. source venv/bin/activate # On Windows use `venv\Scripts\activate`
3. deactivate # To exit the virtual environment

Install the dependencies
1. pip3 install pydantic_ai
2. pip3 install dotenv
3. pip3 install watchdog

You can, however, install dependencies through pip freeze and a requirements.txt file:
1. pip3 freeze > requirements.txt
2. pip3 install -r requirements.txt
"""

import csv
import time
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

load_dotenv()

# Configuration
WATCH_FOLDER = Path("images_watchfolder")
CSV_OUTPUT = Path("concerts.csv")
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


class Concert(BaseModel):
    venue: str
    location: str
    date: str
    event_name: str | None


class BandInfo(BaseModel):
    band_name: str
    concerts: list[Concert]


class ConcertExtraction(BaseModel):
    bands: list[BandInfo]


agent = Agent(
    'openai:gpt-5.2',
    output_type=ConcertExtraction,
    instructions="""
    Extract concert information from the image.
    For each band visible, extract:
    - The band name
    - The venue(s) where they play
    - The location of each venue
    - The date of each concert
    - The event/festival name (if it's part of a named event like a festival)
    If any information is unclear or missing, use "Unknown" as the value.
    Leave event_name as null if there's no specific event/festival name.
    """,
)


def get_media_type(filepath: Path) -> str:
    """Get the MIME type based on file extension"""
    suffix = filepath.suffix.lower()
    media_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    return media_types.get(suffix, 'image/jpeg')


def initialize_csv():
    """Create the CSV file with headers if it doesn't exist"""
    if not CSV_OUTPUT.exists():
        with open(CSV_OUTPUT, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'source_image', 'band_name', 'venue', 'location', 'date', 'event_name'])
        print(f"Created {CSV_OUTPUT}")


def append_to_csv(source_image: str, extraction: ConcertExtraction):
    """Append extracted concert data to the CSV file"""
    timestamp = datetime.now().isoformat()
    
    with open(CSV_OUTPUT, 'a', newline='') as f:
        writer = csv.writer(f)
        for band_info in extraction.bands:
            for concert in band_info.concerts:
                writer.writerow([
                    timestamp,
                    source_image,
                    band_info.band_name,
                    concert.venue,
                    concert.location,
                    concert.date,
                    concert.event_name or ''
                ])
    
    print(f"   Saved to {CSV_OUTPUT}")


def process_image(image_path: Path):
    """Process a single image and extract concert information"""
    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
        return
    
    print(f"\nProcessing: {image_path.name}")
    
    try:
        # Wait a moment to ensure file is fully written
        time.sleep(0.5)
        
        # Read image and send to agent
        image_data = image_path.read_bytes()
        media_type = get_media_type(image_path)
        
        result = agent.run_sync([
            "Extract all concert information from this image.",
            BinaryContent(data=image_data, media_type=media_type),
        ])
        
        # Print results
        for band_info in result.output.bands:
            print(f"   Band: {band_info.band_name}")
            for concert in band_info.concerts:
                event_str = f" ({concert.event_name})" if concert.event_name else ""
                print(f"      Venue: {concert.venue} - {concert.location}{event_str}")
                print(f"      Date: {concert.date}")
        
        # Save to CSV
        append_to_csv(image_path.name, result.output)
        
    except Exception as e:
        print(f"   Error processing {image_path.name}: {e}")


class ImageHandler(FileSystemEventHandler):
    """Handler for new image files in the watch folder"""
    
    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        
        image_path = Path(event.src_path)
        if image_path.suffix.lower() in IMAGE_EXTENSIONS:
            process_image(image_path)


def main():
    # Check that watch folder exists
    if not WATCH_FOLDER.exists():
        raise FileNotFoundError(f"Folder '{WATCH_FOLDER}' not found")
    
    print(f"Watching folder: {WATCH_FOLDER.absolute()}")
    
    # Initialize CSV
    initialize_csv()
    
    # Process any existing images in the folder first
    existing_images = [f for f in WATCH_FOLDER.iterdir() 
                       if f.suffix.lower() in IMAGE_EXTENSIONS]
    if existing_images:
        print(f"\nProcessing {len(existing_images)} existing image(s)...")
        for image_path in existing_images:
            process_image(image_path)
    
    # Set up the watchdog observer
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)
    observer.start()
    
    print(f"\nAgent is now watching for new images. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("Done!")


if __name__ == "__main__":
    main()

# Can I have two agents? A second one adding more information about the bands?
