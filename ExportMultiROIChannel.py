import numpy as np
from PIL import Image
from ORSModel.ors import Channel, StructuredGrid, MultiROI, ROI
import ORSModel
import os
from OrsLibraries.workingcontext import WorkingContext
from OrsPlugins.orsimagesaver import OrsImageSaver
from tkinter import Tk, filedialog


def getNakedNameFromFilePath(name):
	head, tail = os.path.split(name)
	nakedName, fileExtension = os.path.splitext(tail)
	return nakedName


root = Tk()
root.withdraw()
OutputDirectoryName = filedialog.askdirectory(initialdir=r"E:\Google Drive\Research SEM", title="Select output folder for masked png images")
if not OutputDirectoryName:
	quit()

# This line may not work here for the multiROI? Need to look into it if using this again
# Ok, this gets all of them, but you have to manually highlight and select all them
datasetList = WorkingContext.getEntitiesOfClassAsObjects(None, OrsSelectedObjects, Channel.getClassNameStatic())

for dataset in datasetList:
	baseImageName = dataset.getTitle()
	print("image:", baseImageName)
	MultiVertical_channel = Channel()
	progress = ORSModel.ors.Progress()

	MultiVertical_channel = dataset.getAsChannel(MultiVertical_channel, progress)

	# multiVertical_MergedROI.setTitle(newVal='Merged', logging=True)
	# Need something here to deal with all the images in the multiroi
	# nameList = baseImageNameofeachinMultiROIifpossible
	# outChannelList = allchannelsinMultiROI

	imagePath = os.path.join(OutputDirectoryName, baseImageName + '.tiff')
	# pngPath = os.path.join(OutputDirectoryName, baseImageName+'_'+maskName+'.png')
	# This works, but leaves it as 1 and 0, and its a 15 mb image. Lets try to get a binary png? See Below!
	# This outputs all the slices of the dataset already!
	OrsImageSaver.exportDatasetToTiffFile(MultiVertical_channel.getGUID(), imagePath, False, False, False)
	MultiVertical_channel.deleteObjectAndAllItsChildren()

(dirpath, dirnames, rawFileNames) = next(os.walk(OutputDirectoryName))

for name in rawFileNames:
	if name.endswith(('.tiff', '.tif')) and name.find('cropped') == -1:
		print("attempting to convert tiff to png")
		imagePath = os.path.join(dirpath, name)

		fileTypeEnding = imagePath[imagePath.rfind('.'):]
		pngName = name.replace(fileTypeEnding, '.png')
		pngPath = os.path.join(dirpath, pngName)
		rawImage = Image.open(imagePath)
		npRawImage = np.array(rawImage)
		npImage = ((npRawImage / npRawImage.max()) * 255)
		visImage = Image.fromarray(np.uint8(npImage), mode='L')
		visImage.save(pngPath, 'PNG')

