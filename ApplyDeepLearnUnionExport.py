from ORSServiceClass.deepTrainer.deepmodel import DeepModel
from ORSServiceClass.deepTrainer.deepmodelsmanager import DeepModelsManager
import numpy as np
from PIL import Image
from ORSModel.ors import Channel, StructuredGrid, MultiROI, ROI
import ORSModel
from OrsPythonPlugins.OrsGenericMenuItems.menuItems.extractROIs_026bbe94998911e881c30cc47aab53c3 import \
	extractROIs_026bbe94998911e881c30cc47aab53c3 as extractROIs
from OrsHelpers.roihelper import ROIHelper
import os
from OrsLibraries.workingcontext import WorkingContext
from OrsPlugins.orsimagesaver import OrsImageSaver
from tkinter import Tk, filedialog

root = Tk()
root.withdraw()
OutputDirectoryName = filedialog.askdirectory(initialdir="E:\Google Drive\Research SEM", title = "Select output folder for masked png images")
if not OutputDirectoryName:
	quit()

deep_models_manager = DeepModelsManager()
multiVertical_longid = 'U-Net_Unet-MultiVerticalMask-TopDownNanowires_dfd15c8c6b1b11eaa2e0b42e994c3297'
multiVertical_shortid = "dfd15c8c6b1b11eaa2e0b42e994c3297"

snMultVertical_longid = 'U-Net_MultiVertical_WithSn_TopDown_c88d2fb4706d11eab5c1b42e994c3297'
snMultVertical_shortid = "c88d2fb4706d11eab5c1b42e994c3297"

multiVertical_model = deep_models_manager.getDeepModel(multiVertical_shortid, load=True)
snMultVertical_model = deep_models_manager.getDeepModel(snMultVertical_shortid, load=True)

# Ok, this gets all of them, but you have to manually highlight and select all them
channelList = WorkingContext.getEntitiesOfClassAsObjects(None, OrsSelectedObjects, Channel.getClassNameStatic())

for aChannel in channelList:
	baseImageName = aChannel.getTitle()
	print("image:", baseImageName)
	multiVertical_multiROI = MultiROI()
	snMultVertical_multiROI = MultiROI()

	multiVertical_model.apply_model([aChannel], multiVertical_multiROI)
	snMultVertical_model.apply_model([aChannel], snMultVertical_multiROI)

	snMultiVertical_listOfROIs = extractROIs.extractROIsFromMultiROI(sourceDataset=snMultVertical_multiROI)
	snMultiVertical_SnROI = snMultiVertical_listOfROIs[0]
	snMultiVertical_SnROI.setTitle(newVal='Sn', logging=True)
	snMultiVertical_InclinedROI = snMultiVertical_listOfROIs[1]
	snMultiVertical_VerticalROI = snMultiVertical_listOfROIs[2]
	snMultiVertical_MergedROI = snMultiVertical_listOfROIs[3]

	multiVertical_listOfROIs = extractROIs.extractROIsFromMultiROI(sourceDataset=multiVertical_multiROI)
	multiVertical_MergedROI = multiVertical_listOfROIs[0]
	multiVertical_MergedROI.setTitle(newVal='Merged', logging=True)
	multiVertical_VerticalROI = multiVertical_listOfROIs[1]
	multiVertical_VerticalROI.setTitle(newVal='Vertical', logging=True)
	multiVertical_InclinedROI = multiVertical_listOfROIs[2]
	multiVertical_InclinedROI.setTitle(newVal='Inclined', logging=True)

	multiVertical_UnionROI_inputlist = [multiVertical_InclinedROI, multiVertical_VerticalROI, multiVertical_MergedROI]
	multiVertical_UnionROI = ROIHelper.createROIFromStructuredGrid(structuredGridReference=multiVertical_VerticalROI,
	                                                               ROITitle='union',
	                                                               ROIColor=orsColor(r=0.819607843, g=0.31372549,
	                                                                                 b=0.901960784, a=1))
	snSubtracted_ROI = ROIHelper.createROIFromStructuredGrid(structuredGridReference=multiVertical_VerticalROI,
	                                                         ROITitle='SnSubtracted',
	                                                         ROIColor=orsColor(r=0.35, g=0.62, b=0.38, a=1))

	ROIHelper.union(inputROIs=multiVertical_UnionROI_inputlist, destinationROI=multiVertical_UnionROI,
	                keepEmptyLabels=False)

	"""
	Subtracts a ROI or Multi-ROi from another ROi or Multi-ROI, as: destinationROI = firstROI - secondROI.

	The input argument destinationROI cannot be None. If required, create a ROI or a MultiROI prior to calling this method (ex: ROIHelper.createROIFromStructuredGrid).

	:name: subtract
	:execution: execute

	:param firstROI: first ROI or MultiROI
	:type firstROI: ORSModel.ors.ROI, ORSModel.ors.MultiROI
	:param secondROI: second ROI or MultiROI
	:type secondROI: ORSModel.ors.ROI, ORSModel.ors.MultiROI
	:param aROI: ROI or MultiROI of destination
	:type aROI: ORSModel.ors.ROI, ORSModel.ors.MultiROI
	:param keepEmptyLabels: This is only applicable for the situation where the destination is a MultiROI. If False, empty labels of the destination are removed.
	:type keepEmptyLabels: bool
	"""

	ROIHelper.subtract(firstROI=snMultiVertical_SnROI, secondROI=multiVertical_UnionROI, destinationROI=snSubtracted_ROI, keepEmptyLabels=False)

	# snSubtracted_ROI.publish()

	progress = ORSModel.ors.Progress()
	snSubtracted_outchannel = Channel()
	snSubtracted_outchannel = snSubtracted_ROI.getAsChannel(snSubtracted_outchannel, progress)

	vertical_outchannel = Channel()
	vertical_outchannel = multiVertical_VerticalROI.getAsChannel(vertical_outchannel, progress)

	merged_outchannel = Channel()
	merged_outchannel = multiVertical_MergedROI.getAsChannel(merged_outchannel, progress)

	inclined_outchannel = Channel()
	inclined_outchannel = multiVertical_InclinedROI.getAsChannel(inclined_outchannel, progress)

	nameList = ['SurfaceSnMask', 'VerticalMask', 'MergedMask', 'InclinedMask']
	outChannelList = [snSubtracted_outchannel, vertical_outchannel, merged_outchannel, inclined_outchannel]
	for maskName, maskChannel in zip(nameList, outChannelList):
		print('maskname:', maskName, 'maskchannel:', maskChannel)
		imagePath = os.path.join(OutputDirectoryName, baseImageName+'_'+maskName+'.tiff')
		pngPath = os.path.join(OutputDirectoryName, baseImageName+'_'+maskName+'.png')
		# This works, but leaves it as 1 and 0, and its a 15 mb image. Lets try to get a binary png?
		OrsImageSaver.exportDatasetToTiffFile(maskChannel.getGUID(), imagePath, False, False, False)
		rawImage = Image.open(imagePath)
		npImage = np.array(rawImage) * 255
		visImage = Image.fromarray(np.uint8(npImage), mode='L')
		visImage.save(pngPath, 'PNG')
		os.remove(imagePath)
		maskChannel.deleteObjectAndAllItsChildren()



	snMultVertical_multiROI.deleteObjectAndAllItsChildren()
	snMultiVertical_SnROI.deleteObjectAndAllItsChildren()
	snMultiVertical_InclinedROI.deleteObjectAndAllItsChildren()
	snMultiVertical_VerticalROI.deleteObjectAndAllItsChildren()
	snMultiVertical_MergedROI.deleteObjectAndAllItsChildren()

	multiVertical_multiROI.deleteObjectAndAllItsChildren()
	multiVertical_UnionROI.deleteObjectAndAllItsChildren()
	multiVertical_MergedROI.deleteObjectAndAllItsChildren()
	multiVertical_VerticalROI.deleteObjectAndAllItsChildren()
	multiVertical_InclinedROI.deleteObjectAndAllItsChildren()
