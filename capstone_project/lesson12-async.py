r"""
Lesson 11: Pydantic AI agent framework - Extracting structured information from an image, in an agentic way with watch folder.
This time with 2 agents.
The first agent is doing the extraction of the structured information from the image.
The second agent is doing a web search for the genres of each band.

# async version.

Setup:

Always create a virtual environment
1. python -m venv venv
2. source venv/bin/activate # On Windows use `venv\Scripts\activate`
3. deactivate # To exit the virtual environment

Install the dependencies
1. pip3 install pydantic_ai
2. pip3 install dotenv

You can, however, install dependencies through pip freeze and a requirements.txt file:
1. pip3 freeze > requirements.txt
2. pip3 install -r requirements.txt
"""

import asyncio
import csv
from pathlib import Path
from datetime import datetime

from pydantic import BaseModel
from pydantic_ai import Agent, BinaryContent, WebSearchTool
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

load_dotenv()

# Configuration
WATCH_FOLDER = Path("images_watchfolder")
CSV_OUTPUT = Path("concerts-async.csv")
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


class BandEnrichment(BaseModel):
    """Enriched information about a band from web search"""
    genre: str
    country: str


class EnrichedBandInfo(BaseModel):
    """Band info with additional enrichment data"""
    band_name: str
    genre: str
    country: str
    concerts: list[Concert]


class EnrichedConcertExtraction(BaseModel):
    """Concert extraction with enriched band information"""
    bands: list[EnrichedBandInfo]


# Agent 1: Extract concert info from images
extraction_agent = Agent(
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

# Agent 2: Enrich band info with genre and country via web search
enrichment_agent = Agent(
    'openai-responses:gpt-5.2',
    output_type=BandEnrichment,
    builtin_tools=[WebSearchTool()],
    instructions="""
    You are given a band name. Use web search to find information about the band.
    Find:
    - The music genre(s) of the band (e.g., "Rock", "Heavy Metal", "Pop")
    - The country of origin (e.g., "USA", "UK", "Sweden")
    If you cannot find the information, use "Unknown" as the value.
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
            writer.writerow(['timestamp', 'source_image', 'band_name', 'genre', 'country', 'venue', 'location', 'date', 'event_name'])
        print(f"Created {CSV_OUTPUT}")


def append_to_csv(source_image: str, extraction: EnrichedConcertExtraction):
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
                    band_info.genre,
                    band_info.country,
                    concert.venue,
                    concert.location,
                    concert.date,
                    concert.event_name or ''
                ])
    
    print(f"   Saved to {CSV_OUTPUT}")


async def enrich_band(band_info: BandInfo) -> EnrichedBandInfo:
    """Enrich a single band with genre and country info (runs async)"""
    print(f"   Agent 2: Searching web for '{band_info.band_name}' info...")
    
    # Use the enrichment agent to get genre and country
    enrichment_result = await enrichment_agent.run(
        f"Find the genre and country of origin for the band: {band_info.band_name}"
    )
    
    # Create enriched band info
    enriched_band = EnrichedBandInfo(
        band_name=band_info.band_name,
        genre=enrichment_result.output.genre,
        country=enrichment_result.output.country,
        concerts=band_info.concerts
    )
    
    # Print results
    print(f"   Band: {enriched_band.band_name}")
    print(f"      Genre: {enriched_band.genre}")
    print(f"      Country: {enriched_band.country}")
    for concert in enriched_band.concerts:
        event_str = f" ({concert.event_name})" if concert.event_name else ""
        print(f"      Venue: {concert.venue} - {concert.location}{event_str}")
        print(f"      Date: {concert.date}")
    
    return enriched_band


async def process_image(image_path: Path):
    """Process a single image and extract concert information"""
    if image_path.suffix.lower() not in IMAGE_EXTENSIONS:
        return
    
    print(f"\nProcessing: {image_path.name}")
    
    try:
        # Wait a moment to ensure file is fully written
        await asyncio.sleep(0.5)
        
        # Read image and send to extraction agent
        image_data = image_path.read_bytes()
        media_type = get_media_type(image_path)
        
        print("   Agent 1: Extracting concert info from image...")
        extraction_result = await extraction_agent.run([
            "Extract all concert information from this image.",
            BinaryContent(data=image_data, media_type=media_type),
        ])
        
        # Deduplicate bands by name (keep first occurrence, merge concerts)
        unique_bands: dict[str, BandInfo] = {}
        for band_info in extraction_result.output.bands:
            band_name = band_info.band_name.strip().lower()
            if band_name not in unique_bands:
                unique_bands[band_name] = band_info
            else:
                # Merge concerts from duplicate band entries
                unique_bands[band_name].concerts.extend(band_info.concerts)
        
        deduplicated_bands = list(unique_bands.values())
        
        # Enrich ALL bands in parallel using asyncio.gather
        print(f"   Agent 2: Enriching {len(deduplicated_bands)} bands in parallel...")
        enriched_bands = await asyncio.gather(
            *[enrich_band(band_info) for band_info in deduplicated_bands]
        )
        
        # Create enriched extraction result
        enriched_extraction = EnrichedConcertExtraction(bands=list(enriched_bands))
        
        # Save to CSV
        append_to_csv(image_path.name, enriched_extraction)
        
    except Exception as e:
        print(f"   Error processing {image_path.name}: {e}")


class ImageHandler(FileSystemEventHandler):
    """Handler for new image files in the watch folder"""
    
    def on_created(self, event: FileCreatedEvent):
        if event.is_directory:
            return
        
        image_path = Path(event.src_path)
        if image_path.suffix.lower() in IMAGE_EXTENSIONS:
            asyncio.run(process_image(image_path))


async def main():
    # Check that watch folder exists
    if not WATCH_FOLDER.exists():
        raise FileNotFoundError(f"Folder '{WATCH_FOLDER}' not found")
    
    print(f"Watching folder: {WATCH_FOLDER.absolute()}")
    
    # Initialize CSV
    initialize_csv()
    
    # Process any existing images in the folder first (in parallel)
    existing_images = [f for f in WATCH_FOLDER.iterdir() 
                       if f.suffix.lower() in IMAGE_EXTENSIONS]
    if existing_images:
        print(f"\nProcessing {len(existing_images)} existing image(s) in parallel...")
        await asyncio.gather(*[process_image(image_path) for image_path in existing_images])
    
    # Set up the watchdog observer
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(WATCH_FOLDER), recursive=False)
    observer.start()
    
    print(f"\nAgent is now watching for new images. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()
    
    observer.join()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
