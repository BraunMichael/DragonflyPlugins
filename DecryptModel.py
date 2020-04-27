from ORSServiceClass.deepTrainer.deepmodel import DeepModel
from ORSServiceClass.deepTrainer.deepmodelsmanager import DeepModelsManager
import numpy as np
from ORSModel.ors import Channel, StructuredGrid, MultiROI, ROI

deep_models_manager = DeepModelsManager()
deep_models_manager.getGlobalModelsList()
# From output of above
# AdamTestOut_ed76ee34801611ea82ddb42e994c3297
deep_models_manager.decryptModel(r'C:\ProgramData\ORS\Dragonfly41\pythonAllUsersExtensions\PythonPluginExtensions\DeepTrainer\models\AdamTestOut_ed76ee34801611ea82ddb42e994c3297\model.dra',
                                 r'C:\ProgramData\ORS\Dragonfly41\pythonAllUsersExtensions\PythonPluginExtensions\DeepTrainer\models\AdamTestOut_ed76ee34801611ea82ddb42e994c3297\decmodel.h5')
