from icecream import ic
from dataclasses import dataclass
import subprocess
from pathlib import Path
import shutil
import struct
import pyBIG
	
@dataclass(frozen=True)
class IniToBigFile:
	source: Path
	destino: str

def createBigFile(name_of_the_file: Path) -> "pyBIG.Archive":
	# Build header:
	name_of_the_file.parent.mkdir(parents=True, exist_ok=True)
	
	magic = b'BIGF'                          # 4 bytes: 'BIGF'
	archive_size = struct.pack('<I', 16)     # 4 bytes: total size of file
	num_files = struct.pack('<I', 0)         # 4 bytes: number of files
	header_size = struct.pack('<I', 16)      # 4 bytes: offset to first file / dir

	# Combine everything
	header = magic + archive_size + num_files + header_size

	# Save to file
	name_of_the_file.write_bytes(header)

	# read as pyBigArchive and return it
	with open(name_of_the_file, "rb") as f:
		return pyBIG.Archive(f.read())





class Patch:
	def __init__(self: "Patch", from_branch: str, output_to: Path, output_big_name:str):
		self.from_branch = from_branch
		self.output_to = output_to
		self.output_big = output_to / output_big_name 
	def compile(self: "Patch"):
		result = subprocess.run(
			[
				"git",
				"-C", 
				REPOSITORY_ROOT,               # repo location
				"diff",
				"--diff-filter=AM",          # only added/modified
				"--name-only",
				self.from_branch,
				"--", 
				# "1.09v3/"              # folder filter
			],
			capture_output=True,
			text=True
		)
		ic(result)
		input("wait")
		if result.returncode != 0:
			print("Error running git command:", result.stderr)
			exit(1)
			
		iniList: list[IniToBigFile] = []
		datList: list[str] = []
		
		for file_str in result.stdout.splitlines():
			print(file_str)
			if file_str.startswith(r"1.09v3/data") or file_str.startswith(r"1.09v3/art"):
				iniList.append(IniToBigFile(
					source = REPOSITORY_ROOT/file_str,
					destino = file_str.replace("1.09v3/", "").replace("/","\\")
				))
					
			elif file_str.endswith(".dat") or file_str.endswith("plash.jpg"):
				datList.append(file_str)
			
			else:
				print(f"{file_str} skipped")
		# ic(iniList)
		self.process_iniList(iniList)
		self.process_datList(datList)
	
	def process_iniList(self: "Patch", iniList: list[IniToBigFile]):
		archive = createBigFile(self.output_big)
		# ic(iniList)
		for file in iniList:
			if not file.source.exists():
				print(f"Error: {file.source} doesn't exist")
			else:
				if file.source.suffix in (".ini", ".map", ".tga", ".inc", ".str", ".dds", ".jpg"): #Just one extra safety filter!
					archive.add_file(file.destino, file.source.read_bytes())
				else:
					print(f"Skipped {file.source}")
					
		archive.repack()
		# ic(self.output_big)
		archive.save(str(self.output_big))
		print(f"Success building {self.output_big}")

	def process_datList(self: "Patch", datList: list[str] ):
		for item in datList:
			source = REPOSITORY_ROOT / item
			destino = self.output_to / (item.replace("1.09v3/",""))
			destino.parent.mkdir(parents=True, exist_ok=True)
			if source.exists():
				shutil.copy2(source, destino)
			else:
				print(f"ERROR: {source} doesn't exist")
				
	def process_to_big(self: "Patch", path: Path) -> str:
		relative_to = "art"
		s = str(path)
		idx = s.lower().find(relative_to.lower())  # case-insensitive search
		if idx == -1:
			raise ValueError(f"'{relative_to}' not found in {path}")
		subpath = s[idx:]
		return subpath.replace("/", "\\")
		



if __name__ == "__main__":
	REPOSITORY_ROOT = Path(r"D:\WholeBFME2")
	patch_v301 = Patch(
		from_branch = "109v200",
		# to_branch = "109v302",
		output_to = Path(r"D:\WholeBFME2"),
		output_big_name = "##!__BT2DC-v1.09v3.02.big",
	)
	
	patch_v301.compile()