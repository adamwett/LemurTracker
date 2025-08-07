# update_paths.py
from src.database.database_handler import DatabaseHandler
from src.database.models import ProcessedVideo

def update_file_paths():
    db = DatabaseHandler()
    session = db.Session()
    
    try:
        # Get all videos
        videos = session.query(ProcessedVideo).all()
        print(f"Found {len(videos)} videos to update")
        
        old_base = "/Users/sammcconnellscomputer/Desktop/senior-design-stuff/2025Spring-Team16-Zoo/backend"
        new_base = "/Users/seanturner/Downloads/2025Spring-Team16-Zoo/backend"
        
        updated_count = 0
        for video in videos:
            if video.filepath.startswith(old_base):
                # Replace the base path
                new_path = video.filepath.replace(old_base, new_base)
                print(f"Updating: {video.filepath}")
                print(f"     To: {new_path}")
                
                video.filepath = new_path
                updated_count += 1
        
        # Commit changes
        session.commit()
        print(f"Successfully updated {updated_count} file paths")
        
    except Exception as e:
        session.rollback()
        print(f"Error updating paths: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_file_paths()