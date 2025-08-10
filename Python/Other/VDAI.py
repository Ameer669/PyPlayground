import yt_dlp
import os
import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import re

class UltimateVideoDownloader:
    def __init__(self, base_path=r"C:\Users\hp OMEN\Downloads\Video"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        self.download_history = self.base_path / "download_history.json"
        self.load_history()
        
    def load_history(self):
        """Load download history"""
        try:
            if self.download_history.exists():
                with open(self.download_history, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except:
            self.history = []
    
    def save_history(self, url, title, path, quality, size_mb):
        """Save download to history"""
        record = {
            'url': url,
            'title': title,
            'path': str(path),
            'quality': quality,
            'size_mb': size_mb,
            'date': datetime.now().isoformat()
        }
        self.history.append(record)
        
        with open(self.download_history, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def check_aria2c(self):
        """Check if aria2c is available"""
        try:
            subprocess.run(['aria2c', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def sanitize_filename(self, filename):
        """Clean filename for safe saving"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'[\n\r\t]', ' ', filename)
        return filename[:200]  # Limit length
    
    def get_video_info(self, url):
        """Get comprehensive video information"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'uploader': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'upload_date': info.get('upload_date', ''),
                    'description': info.get('description', '')[:500] + '...',
                    'thumbnail': info.get('thumbnail'),
                    'formats': info.get('formats', []),
                    'webpage_url': info.get('webpage_url', url)
                }
        except Exception as e:
            print(f"❌ Failed to get video info: {e}")
            return None
    
    def show_video_info(self, info):
        """Display detailed video information"""
        if not info:
            return
            
        print("\n" + "="*60)
        print(f"📺 TITLE: {info['title']}")
        print(f"👤 UPLOADER: {info['uploader']}")
        print(f"⏱️  DURATION: {info['duration']} seconds ({info['duration']//60}:{info['duration']%60:02d})")
        print(f"👁️  VIEWS: {info['view_count']:,}" if info['view_count'] else "👁️  VIEWS: Unknown")
        print(f"📅 UPLOAD DATE: {info['upload_date']}")
        print(f"📝 DESCRIPTION: {info['description']}")
        print("="*60)
    
    def get_available_qualities(self, formats):
        """Extract and organize available video qualities"""
        video_formats = []
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none':  # Skip audio-only
                height = fmt.get('height', 0)
                width = fmt.get('width', 0)
                filesize = fmt.get('filesize', 0)
                fps = fmt.get('fps', 0)
                vcodec = fmt.get('vcodec', 'unknown')
                acodec = fmt.get('acodec', 'unknown')
                tbr = fmt.get('tbr', 0)  # Total bitrate
                vbr = fmt.get('vbr', 0)  # Video bitrate
                
                quality_info = {
                    'format_id': fmt.get('format_id'),
                    'resolution': f"{width}x{height}" if width and height else "Unknown",
                    'fps': fps,
                    'ext': fmt.get('ext', 'mp4'),
                    'filesize': filesize,
                    'size_mb': filesize / (1024 * 1024) if filesize else 0,
                    'vcodec': vcodec,
                    'acodec': acodec,
                    'quality_note': fmt.get('format_note', ''),
                    'tbr': tbr,
                    'vbr': vbr,
                    'quality_score': self.calculate_quality_score(height, tbr, vbr, vcodec)
                }
                video_formats.append(quality_info)
        
        # Sort by quality score (best first), then resolution, then bitrate
        video_formats.sort(key=lambda x: (
            x['quality_score'],
            int(x['resolution'].split('x')[1]) if 'x' in x['resolution'] and x['resolution'].split('x')[1].isdigit() else 0,
            x['tbr']
        ), reverse=True)
        
        return video_formats
    
    def calculate_quality_score(self, height, tbr, vbr, vcodec):
        """Calculate quality score for format ranking"""
        score = 0
        
        # Resolution score (higher is better)
        if height >= 1080:
            score += 100
        elif height >= 720:
            score += 80
        elif height >= 480:
            score += 60
        elif height >= 360:
            score += 40
        else:
            score += 20
        
        # Bitrate score (higher is better, but diminishing returns)
        if tbr > 0:
            score += min(tbr / 100, 50)  # Cap at 50 points
        if vbr > 0:
            score += min(vbr / 100, 30)  # Cap at 30 points
        
        # Codec quality bonus
        if 'avc1' in vcodec.lower() or 'h264' in vcodec.lower():
            score += 20  # H.264 is widely compatible and good quality
        elif 'av01' in vcodec.lower():
            score += 25  # AV1 is newer and more efficient
        elif 'vp9' in vcodec.lower():
            score += 15  # VP9 is good but less compatible
        
        return score
    
    def display_quality_menu(self, formats):
        """Display quality selection menu"""
        print("\n🎯 AVAILABLE QUALITIES:")
        print("-" * 80)
        print(f"{'#':<3} {'Resolution':<12} {'FPS':<5} {'Size':<10} {'Bitrate':<8} {'Codec':<10} {'Note':<15}")
        print("-" * 80)
        
        for i, fmt in enumerate(formats[:15], 1):  # Show top 15
            size_str = f"{fmt['size_mb']:.1f}MB" if fmt['size_mb'] > 0 else "Unknown"
            fps_str = f"{fmt['fps']}" if fmt['fps'] else "N/A"
            codec_str = f"{fmt['vcodec'][:8]}"
            bitrate_str = f"{fmt['tbr']:.0f}k" if fmt['tbr'] > 0 else "N/A"
            
            print(f"{i:<3} {fmt['resolution']:<12} {fps_str:<5} {size_str:<10} {bitrate_str:<8} {codec_str:<10} {fmt['quality_note'][:15]}")
        
        print(f"{len(formats) + 1:<3} {'AUTO-HQ':<12} {'N/A':<5} {'Smart':<10} {'Best':<15} {'Best quality ≤1080p'}")
        print(f"{len(formats) + 2:<3} {'AUTO-FAST':<12} {'N/A':<5} {'Fast':<10} {'Compatible':<15} {'Fast download ≤1080p'}")
        print("0   CANCEL")
        print("-" * 80)
    
    def display_audio_menu(self):
        """Display audio download options menu"""
        print("\n🎵 AUDIO DOWNLOAD OPTIONS:")
        print("-" * 60)
        print("1. ⚡ Ultra Fast (original format - m4a/webm/opus)")
        print("2. 🎵 Fast MP3 (128kbps - quick conversion)")
        print("3. 🎧 High Quality MP3 (320kbps)")
        print("4. 📻 Standard MP3 (192kbps)")
        print("0. ❌ Cancel")
        print("-" * 60)
    
    def progress_hook(self, d):
        """Enhanced progress display"""
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', 'N/A').strip()
                speed = d.get('_speed_str', 'N/A').strip()
                eta = d.get('_eta_str', 'N/A').strip()
                downloaded = d.get('_downloaded_bytes_str', '').strip()
                total = d.get('_total_bytes_str', '').strip()
                
                progress_line = f"⬇️  {percent} | Speed: {speed} | ETA: {eta} | Downloaded: {downloaded}/{total}"
                print(f"\r{progress_line}", end='', flush=True)
            except:
                print("⬇️  Downloading...", end='', flush=True)
                
        elif d['status'] == 'finished':
            filename = os.path.basename(d['filename'])
            print(f"\n✅ Download completed: {filename}")
    
    def ultra_fast_audio_download(self, url, output_path=None):
        """Download audio in original format (no conversion) - FASTEST"""
        if not output_path:
            output_path = self.base_path / "Audio"
        
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # ULTRA-FAST: No conversion at all
        options = {
            # Download best audio in original format (m4a/webm/opus)
            'format': 'bestaudio',
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            
            # Maximum speed settings
            'concurrent_fragments': 16,
            'http_chunk_size': 20971520,
            'retries': 2,
            'fragment_retries': 2,
            
            # Skip ALL processing
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'extract_flat': False,
            'postprocessors': [],  # NO conversion
        }
        
        # aria2c for maximum speed
        if self.check_aria2c():
            options.update({
                'external_downloader': 'aria2c',
                'external_downloader_args': {
                    'aria2c': [
                        '--max-connection-per-server=16',
                        '--split=16',
                        '--min-split-size=500K',
                        '--continue=true'
                    ]
                }
            })
        
        try:
            print("⚡ Ultra-fast audio download (original format)...")
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            print("✅ Ultra-fast audio download completed!")
            print("📁 Note: File might be .m4a, .webm, or .opus format")
            return True
        except Exception as e:
            print(f"❌ Ultra-fast audio download failed: {e}")
            return False
    
    def fast_audio_download(self, url, quality='128', output_path=None):
        """Fast audio download with MP3 conversion"""
        if not output_path:
            output_path = self.base_path / "Audio"
        
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # SPEED-OPTIMIZED audio options
        options = {
            # Download ONLY audio stream (no video conversion needed)
            'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            
            # Speed optimizations
            'concurrent_fragments': 8,
            'http_chunk_size': 20971520,  # 20MB chunks
            'retries': 3,
            'fragment_retries': 3,
            
            # Skip everything unnecessary
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': False,
            'extract_flat': False,
            
            # FAST conversion settings
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
        }
        
        # Use aria2c if available
        if self.check_aria2c():
            options.update({
                'external_downloader': 'aria2c',
                'external_downloader_args': {
                    'aria2c': [
                        '--max-connection-per-server=8',
                        '--split=8',
                        '--min-split-size=1M',
                        '--continue=true',
                        '--max-tries=3'
                    ]
                }
            })
        
        try:
            quality_name = f"Fast MP3 ({quality}kbps)"
            print(f"🎵 {quality_name} download starting...")
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            print(f"✅ {quality_name} download completed!")
            return True
        except Exception as e:
            print(f"❌ Audio download failed: {e}")
            return False
    
    def download_audio_with_menu(self, url):
        """Download audio with quality selection menu"""
        # Get video info first
        print("🔍 Analyzing video...")
        info = self.get_video_info(url)
        if not info:
            return False
        
        # Show video info
        self.show_video_info(info)
        
        # Create organized folder structure
        platform = self.detect_platform(url)
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = self.base_path / "Audio" / platform / today
        
        # Show audio menu
        self.display_audio_menu()
        
        try:
            choice = input("Choose audio option (0-4): ").strip()
            
            if choice == '0':
                print("❌ Audio download cancelled")
                return False
            elif choice == '1':
                # Ultra fast - no conversion
                success = self.ultra_fast_audio_download(url, output_dir)
                quality_note = "Ultra Fast (Original Format)"
            elif choice == '2':
                # Fast MP3 - 128kbps
                success = self.fast_audio_download(url, '128', output_dir)
                quality_note = "Fast MP3 (128kbps)"
            elif choice == '3':
                # High quality MP3 - 320kbps
                success = self.fast_audio_download(url, '320', output_dir)
                quality_note = "High Quality MP3 (320kbps)"
            elif choice == '4':
                # Standard MP3 - 192kbps
                success = self.fast_audio_download(url, '192', output_dir)
                quality_note = "Standard MP3 (192kbps)"
            else:
                print("❌ Invalid choice, using fast MP3")
                success = self.fast_audio_download(url, '128', output_dir)
                quality_note = "Fast MP3 (128kbps)"
            
            if success:
                # Save to history
                file_size = self.get_file_size(output_dir / f"{self.sanitize_filename(info['title'])}.*")
                self.save_history(url, info['title'], str(output_dir), quality_note, file_size)
                print(f"🎉 SUCCESS! Audio saved to: {output_dir}")
            
            return success
            
        except Exception as e:
            print(f"❌ Audio download failed: {e}")
            return False
    
    def download_video(self, url, quality_choice=None, audio_only=False):
        """Enhanced download with all features"""
        
        # Get video info
        print("🔍 Analyzing video...")
        info = self.get_video_info(url)
        if not info:
            return False
        
        # Show video info
        self.show_video_info(info)
        
        # Check if already downloaded
        for record in self.history:
            if record['url'] == url:
                print(f"⚠️  Already downloaded on {record['date'][:10]}")
                choice = input("Download again? (y/n): ").lower()
                if choice != 'y':
                    return False
        
        # If audio only, use the dedicated audio menu
        if audio_only:
            return self.download_audio_with_menu(url)
        
        # Setup quality for video
        if quality_choice is None:
            formats = self.get_available_qualities(info['formats'])
            if not formats:
                print("❌ No video formats found")
                return False
            
            self.display_quality_menu(formats)
            
            try:
                choice = int(input(f"\n🎯 Choose quality (1-{len(formats) + 2}): "))
                
                if choice == 0:
                    print("❌ Download cancelled")
                    return False
                elif choice == len(formats) + 1:
                    # High Quality Auto - prioritize quality over speed
                    format_selector = 'best[height<=1080][vcodec^=avc1]/best[height<=1080][vcodec^=h264]/best[height<=1080]/best'
                    quality_note = "Auto High Quality (≤1080p)"
                elif choice == len(formats) + 2:
                    # Fast Auto - prioritize speed/compatibility
                    format_selector = 'best[height<=1080][ext=mp4]/best[height<=1080]/best'
                    quality_note = "Auto Fast (≤1080p)"
                elif 1 <= choice <= len(formats):
                    selected_format = formats[choice - 1]
                    format_selector = selected_format['format_id']
                    quality_note = f"{selected_format['resolution']} ({selected_format['ext']})"
                else:
                    print("❌ Invalid choice, using auto high quality")
                    format_selector = 'best[height<=1080][vcodec^=avc1]/best[height<=1080][vcodec^=h264]/best[height<=1080]/best'
                    quality_note = "Auto High Quality (≤1080p)"
            except ValueError:
                print("❌ Invalid input, using auto high quality")
                format_selector = 'best[height<=1080][vcodec^=avc1]/best[height<=1080][vcodec^=h264]/best[height<=1080]/best'
                quality_note = "Auto High Quality (≤1080p)"
        else:
            format_selector = quality_choice
            quality_note = "Custom"
        
        # Create organized folder structure
        platform = self.detect_platform(url)
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = self.base_path / "Video" / platform / today
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean filename
        clean_title = self.sanitize_filename(info['title'])
        output_template = str(output_dir / f"{clean_title}.%(ext)s")
        
        # Setup download options
        use_aria2c = self.check_aria2c()
        
        options = {
            'format': format_selector,
            'outtmpl': output_template,
            'progress_hooks': [self.progress_hook],
            'ignoreerrors': True,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'writethumbnail': True,  # Save thumbnail
        }
        
        # Speed optimizations
        if use_aria2c:
            print("🚀 Using aria2c for maximum speed!")
            options.update({
                'external_downloader': 'aria2c',
                'external_downloader_args': {
                    'aria2c': [
                        '--max-connection-per-server=16',
                        '--split=16',
                        '--min-split-size=1M',
                        '--max-concurrent-downloads=8',
                        '--continue=true',
                        '--max-tries=3',
                        '--retry-wait=1'
                    ]
                }
            })
        else:
            options.update({
                'concurrent_fragments': 8,
                'http_chunk_size': 20971520,
                'retries': 3,
                'fragment_retries': 3,
            })
        
        # Download
        print(f"\n🎬 Starting download: {quality_note}")
        print(f"📁 Saving to: {output_dir}")
        
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([url])
            
            # Save to history
            file_size = self.get_file_size(output_dir / f"{clean_title}.*")
            self.save_history(url, info['title'], str(output_dir), quality_note, file_size)
            
            print(f"🎉 SUCCESS! Downloaded to: {output_dir}")
            return True
            
        except Exception as e:
            print(f"\n❌ Download failed: {e}")
            return False
    
    def detect_platform(self, url):
        """Detect social media platform"""
        domain = urlparse(url).netloc.lower()
        
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return 'YouTube'
        elif 'instagram.com' in domain:
            return 'Instagram'
        elif 'tiktok.com' in domain:
            return 'TikTok'
        elif 'twitter.com' in domain or 'x.com' in domain:
            return 'Twitter'
        elif 'facebook.com' in domain:
            return 'Facebook'
        else:
            return 'Other'
    
    def get_file_size(self, pattern):
        """Get file size in MB"""
        try:
            for file_path in Path().glob(str(pattern)):
                if file_path.is_file():
                    return file_path.stat().st_size / (1024 * 1024)
        except:
            pass
        return 0
    
    def show_history(self):
        """Show download history"""
        if not self.history:
            print("📝 No download history found")
            return
        
        print("\n📚 DOWNLOAD HISTORY:")
        print("-" * 100)
        
        for i, record in enumerate(reversed(self.history[-10:]), 1):  # Last 10
            date = record['date'][:10]
            title = record['title'][:50] + "..." if len(record['title']) > 50 else record['title']
            quality = record['quality']
            size = f"{record['size_mb']:.1f}MB" if record['size_mb'] > 0 else "Unknown"
            
            print(f"{i:2}. [{date}] {title}")
            print(f"    Quality: {quality} | Size: {size}")
            print(f"    Path: {record['path']}")
            print()
    
    def batch_download(self, urls, download_type='video'):
        """Download multiple videos or audio files"""
        print(f"🎯 Batch downloading {len(urls)} {download_type}s...")
        results = []
        
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*20} {download_type.upper()} {i}/{len(urls)} {'='*20}")
            if download_type == 'audio':
                result = self.download_audio_with_menu(url)
            else:
                result = self.download_video(url, quality_choice='best[height<=1080][vcodec^=avc1]/best[height<=1080][vcodec^=h264]/best[height<=1080]/best')
            results.append(result)
        
        successful = sum(results)
        print(f"\n🎉 Batch complete: {successful}/{len(urls)} successful")
        return results

def main():
    """Main interface"""
    downloader = UltimateVideoDownloader()
    
    while True:
        print("\n" + "="*60)
        print("🚀 ULTIMATE VIDEO & AUDIO DOWNLOADER")
        print("="*60)
        print("1. 📥 Download single video")
        print("2. 🎵 Download audio only")
        print("3. 📦 Batch download videos")
        print("4. 🎼 Batch download audio")
        print("5. ⚡ Quick audio download menu")
        print("6. 📚 View history")
        print("7. ❌ Exit")
        print("-" * 60)
        
        try:
            choice = input("Choose option (1-7): ").strip()
            
            if choice == '1':
                url = input("\n📎 Enter video URL: ").strip()
                if url:
                    downloader.download_video(url)
                else:
                    print("❌ Invalid URL")
            
            elif choice == '2':
                url = input("\n📎 Enter video URL for audio: ").strip()
                if url:
                    downloader.download_audio_with_menu(url)
                else:
                    print("❌ Invalid URL")
            
            elif choice == '3':
                urls = []
                print("\n📦 Enter video URLs (press Enter twice to finish):")
                while True:
                    url = input("URL: ").strip()
                    if not url:
                        break
                    urls.append(url)
                
                if urls:
                    downloader.batch_download(urls, 'video')
                else:
                    print("❌ No URLs provided")
            
            elif choice == '4':
                urls = []
                print("\n🎼 Enter URLs for audio download (press Enter twice to finish):")
                while True:
                    url = input("URL: ").strip()
                    if not url:
                        break
                    urls.append(url)
                
                if urls:
                    downloader.batch_download(urls, 'audio')
                else:
                    print("❌ No URLs provided")
            
            elif choice == '5':
                print("\n⚡ QUICK AUDIO DOWNLOAD")
                print("=" * 40)
                print("1. ⚡ Ultra Fast (original format)")
                print("2. 🎵 Fast MP3 (128kbps)")
                print("3. 🎧 High Quality MP3 (320kbps)")
                print("-" * 40)
                
                url = input("Enter video URL: ").strip()
                if not url:
                    print("❌ Invalid URL")
                    continue
                
                quick_choice = input("Choose option (1-3): ").strip()
                output_dir = downloader.base_path / "Audio"
                
                if quick_choice == '1':
                    downloader.ultra_fast_audio_download(url, output_dir)
                elif quick_choice == '2':
                    downloader.fast_audio_download(url, '128', output_dir)
                elif quick_choice == '3':
                    downloader.fast_audio_download(url, '320', output_dir)
                else:
                    print("❌ Invalid choice")
            
            elif choice == '6':
                downloader.show_history()
            
            elif choice == '7':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()