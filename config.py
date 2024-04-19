from datetime import *

urls = {
    "buy": "https://cdn-icons-png.flaticon.com/512/825/825575.png",
    "sell": "https://images.squarespace-cdn.com/content/v1/572fc6042b8dde9e10b6ea9d/1491097100995-615THMM0INP9EHRM043Z/How+To+Sell+Your+Shares.jpg?format=1000w",
    "flow":"https://logopond.com/logos/f701750e9ae9f6c2b31dfd3c0c472955.png",
    "exclusion": "https://i.pinimg.com/736x/e2/ea/3d/e2ea3d656e7f600c7c1045e89bd858b1.jpg",
    "stat": "https://media.istockphoto.com/id/1323424355/ru/%D0%B2%D0%B5%D0%BA%D1%82%D0%BE%D1%80%D0%BD%D0%B0%D1%8F/%D0%B7%D0%BD%D0%B0%D1%87%D0%BE%D0%BA-money-chart-vector-%D1%81%D1%82%D0%B0%D1%82%D0%B8%D1%81%D1%82%D0%B8%D0%BA%D0%B0-%D0%B4%D0%B5%D0%BD%D0%B5%D0%B3-%D1%81-%D0%B4%D0%B8%D0%B0%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%BE%D0%B9-%D0%B1%D0%B0%D1%80-%D1%80%D0%B0%D1%81%D1%82%D0%B5%D1%82-%D1%80%D0%BE%D1%81%D1%82-%D0%B8-%D0%BF%D0%B0%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80%D0%B0.jpg?s=612x612&w=0&k=20&c=T6qGN4G_0M58qMoSvhkWdod3GZwQceaA2SdWG-Qbeys="
}

hour = (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%d")
day = (datetime.now() - timedelta(weeks=5)).strftime("%Y-%m-%d")

