
from .controller.feedhistory import *
from .controller.pond import *
from .controller.feedtype import *
from .controller.pondactivation import *
from .controller.fishdeath import *
from .controller.fishtransfer import *
from .controller.fishsort import *
from .controller.fishgrading import *
from .controller.dailywaterquality import *
from .controller.weeklywaterquality import *
from .controller.pondtreatment import *
from .controller.statistic import *
from .controller.authentication import *
from .controller.breeder import *
from .controller.farm import *
from .controller.inventories import *
from .controller.history import *
from .controller.logging import *
from .controller.addfish import *
from .controller.fishharvestprice import *
from .controller.feeddistribution import *
from .controller.upload import *
from .controller.treatmentdistribution import *

def initialize_routes(api):

    # pond
    api.add_resource(PondsApi, '/api/ponds')
    api.add_resource(PondApi, '/api/ponds/<id>')
    api.add_resource(PondImageApi, '/api/ponds/image/<id>')
    api.add_resource(PondImageApiDummy, '/api/ponds/image')

    # pond status
    api.add_resource(PondsStatusApi, '/api/ponds/status')
    api.add_resource(PondStatusApi, '/api/ponds/status/<pond_id>')
    api.add_resource(PondActivationApi, '/api/ponds/<pond_id>/activation')
    api.add_resource(PondDeactivationApi, '/api/ponds/<pond_id>/closing')

    # feedtype
    # api.add_resource(FeedTypesApi, '/api/feedtypes')
    # api.add_resource(FeedTypeApi, '/api/feedtypes/<id>')
    api.add_resource(PondActivationDetailApi, '/api/pondactivation/<id>/<pond>')

    # feedhistory
    api.add_resource(FeedHistorysApi, '/api/feedhistorys')
    api.add_resource(FeedHistoryApi, '/api/feedhistorys/<id>')
    api.add_resource(FeedHistoryMonthByActivation,
                     '/api/feedhistorys/month/<activation_id>')
    api.add_resource(FeedHistoryWeekByActivation,
                     '/api/feedhistorys/week/<activation_id>/<month>')
    api.add_resource(FeedHistoryDayByActivation,
                     '/api/feedhistorys/day/<activation_id>/<week>')
    api.add_resource(FeedHistoryHourByActivation,
                     '/api/feedhistorys/hour/<activation_id>/<day>')
    api.add_resource(FeedHistoryByPond,
                     '/api/feedhistorysbypond')
    api.add_resource(FeedHistoryByOnePond,
                     '/api/feedhistorysbyonepond/<id>')
    api.add_resource(FeedHistoryForChart,
                     '/api/feedhistoryforchart')
    
    # feed distribution
    api.add_resource(FeedDistributionApi, '/api/feeddistribution')

    # image upload
    api.add_resource(UploadImageApi, '/api/uploadimage')

    # fish death
    api.add_resource(FishDeathsApi, '/api/fishdeath')
    api.add_resource(FishDeathApi, '/api/fishdeath/<id>')
    api.add_resource(FishDeathsApiByActivation,
                     '/api/fishdeath/activation/<activation_id>')
    api.add_resource(FishDeathImageApi, '/api/fishdeath/image/<id>')
    api.add_resource(FishDeathImageApiDummy, '/api/fishdeath/image')

    # fish transfer
    api.add_resource(FishTransfersApi, '/api/fishtransfer')
    api.add_resource(FishTransferApi, '/api/fishtransfer/<id>')

    # add fish
    api.add_resource(AddFishApi, '/api/addfish')

    # edit fish
    api.add_resource(EditFishApi, '/api/editfish')

    # fish sort
    api.add_resource(FishSortsApi, '/api/fishsort')


    # fish grading
    api.add_resource(FishGradingsApi, '/api/fishgradings')
    api.add_resource(FishGradingApi, '/api/fishgradings/<id>')
    api.add_resource(FishGradingApiByActivation,
                     '/api/fishgradings/activation/<activation_id>')
    # graph
    api.add_resource(FishGradingGraphApi,
                     '/api/fishgradings/graph/<activationOrPondId>', endpoint='api.graph')

    # daily water
    api.add_resource(DailyWaterQualitysApi, '/api/dailywaterquality')
    api.add_resource(DailyWaterQualityApi, '/api/dailywaterquality/<id>')

    # weekly water
    api.add_resource(WeeklyWaterQualitysApi, '/api/weeklywaterquality')
    api.add_resource(WeeklyWaterQualityApi, '/api/weeklywaterquality/<id>')

    # pond treatment
    api.add_resource(PondTreatmentsApi, '/api/pondtreatment')
    api.add_resource(PondTreatmentApi, '/api/pondtreatment/<id>')

    # pond treatment distribution
    api.add_resource(TreatmentDistributionApi, '/api/treatmentdistribution')
    
    # StatisticAPI
    api.add_resource(StatisticApi, '/api/statistic')

    #user
    api.add_resource(BreederApi, '/api/breeder')
    api.add_resource(FarmApi, '/api/farm')
    api.add_resource(Login, '/api/login')
    api.add_resource(Register, '/api/register')

    # seed inventory
    api.add_resource(SeedInventoriesApi, '/api/inventory/seed')
    api.add_resource(SeedInventoryApi, '/api/inventory/seed/<id>')

    # feed inventory
    api.add_resource(FeedInventoriesApi, '/api/inventory/feed')
    api.add_resource(FeedInventoryApi, '/api/inventory/feed/<id>')
    api.add_resource(FeedNamesApi, '/api/inventory/feed/name')
    api.add_resource(FeedNameApi, '/api/inventory/feed/name/<id>')

    # suplemen inventory
    api.add_resource(SuplemenInventoriesApi, '/api/inventory/suplemen')
    api.add_resource(SuplemenInventoryApi, '/api/inventory/suplemen/<id>')

    # electric inventory
    api.add_resource(ElectricInventoriesApi, '/api/inventory/electric')
    api.add_resource(ElectricInventoryApi, '/api/inventory/electric/<id>')

    # asset inventory
    api.add_resource(AssetInventoriesApi, '/api/inventory/asset')
    api.add_resource(AssetInventoryApi, '/api/inventory/asset/<id>')

    # history
    api.add_resource(SeedHistoryApi, '/api/history/inventory/seed')
    api.add_resource(FeedFishHistoryApi, '/api/history/inventory/feed')
    api.add_resource(SuplemenHistoryApi, '/api/history/inventory/suplemen')
    api.add_resource(BreederListApi, '/api/breederlist')
    api.add_resource(LoggingApi, '/api/logging')

    # chart fish
    api.add_resource(FishLiveChart, '/api/fishchart/<activation_id>')

    # deactivation recap
    api.add_resource(DeactivationRecapApi, '/api/recap/deactivation')

    # fish harvested price
    api.add_resource(FishHarvestedPriceApi, '/api/fishharvestedprice')
    api.add_resource(FishHarvestedPriceApibyId, '/api/fishharvestedprice/<id>')

    api.add_resource(GetPricesApi, '/api/prices/<activation_id>')