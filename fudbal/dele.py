from pathlib import Path

folder = Path('/content/kvote-backend/csv')


def delete(): 
  for fajl in folder.glob("*.csv"):
      fajl.unlink()  # briše fajl
            
