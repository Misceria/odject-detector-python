/********************************************************************************
 * ArchiveWindow - Main window for archive viewer application.
 *
 * @file    ArchiveWindow.cpp
 * @author  Mr-Walrus <mr.walrus26@gmail.com>
 * @brief   This file contains the declaration of the ArchiveWindow class, which
 *          represents the main window for the archive viewer application. It
 *          provides functionality for viewing archived data and managing user
 *          interactions.
 * @date    March 14, 2024
 * @license BSD
 ********************************************************************************/

#include "stdafx.h"
#include "ArchiveWindow.h"
#include "iostream"
#include "string"

ArchiveWindow::ArchiveWindow(QWidget *parent)
	: QMainWindow(parent) {
	ui.setupUi(this);


	QSettings settings("SpSpApp", "SpSpAppSettings");
	QSqlDatabase sdb = QSqlDatabase::addDatabase("QSQLITE");
	sdb.setDatabaseName(settings.value("DBName").toString());
	if (!sdb.open()) 
		qDebug() <<"db_open_err";
	else
		qDebug() <<"db_open";

	//QSqlQuery query;
	//qDebug() << query.exec("SELECT * FROM Records");
	//QSqlRecord rec = query.record();
	//int OC_number = 0;
	//int Cam_number = 0;
	//QString Record_date = "";
	//QString File_name = "";
	//QString File_type = "";

	////QString c1 = "";
	////int c2 = 0;

	////QString str = "CREATE TABLE \"Records\" (\"Record_date\" DATETIME NOT NULL, \"OC_number\" INTEGER NOT NULL, \"Cam_number\" INTEGER NOT NULL, \"File_name\" TEXT NOT NULL, \"File_type\" TEXT NOT NULL);";
	////qDebug() << query.exec(str);

	//while (query.next()) {
	//	//c1 = query.value(rec.indexOf("column1")).toString();
	//	//c2 = query.value(rec.indexOf("column2")).toInt();

	//	//qDebug() << "c1 " << c1
	//	//	<< ". c2" << c2;
	//	
	//	Record_date = query.value(rec.indexOf("Record_date")).toString();
	//	OC_number = query.value(rec.indexOf("OC_number")).toInt();
	//	Cam_number = query.value(rec.indexOf("Cam_number")).toInt();
	//	File_name = query.value(rec.indexOf("File_name")).toString();
	//	File_type = query.value(rec.indexOf("File_type")).toString();

	//	qDebug() << "Record_date " << Record_date
	//		<< ". OC_number " << OC_number
	//		<< ". Cam_number " << Cam_number
	//		<< ". File_name " << File_name
	//		<< ". File_type" << File_type;
	//}


	QSqlQuery query;

	// получаем значения всех checkbox'ов для создания правильного sql-запроса
	string request = "SELECT * FROM Records r WHERE";
	bool first = True;
	if (camVD1_CB->isChecked()){
		string request = request + 'r.Cam_number == "1"';
		bool first = False;
	}
	if (camVD2_CB->isChecked()){
		if (first){
			string request = request + 'r.Cam_number == "2"';
		}
		else{
			string request = request + 'OR r.Cam_number == "2"';
		}
	}
	//if (camIK1_CB->isChecked()){
	//	string request = request + 'r.Cam_number == "1"';
	//	bool first = False;
	//}
	//if (camIK2_CB->isChecked()){
	//	if (bool){
	//		string request = request + 'r.Cam_number == "0"';
	//	}
	//	else{
	//		string request = request + 'OR r.Cam_number == "0	"';
	//	}
	//}
	if (vid_CB.isChecked()){
		if (first){
			string request = request + 'r.File_type == "AVI" OR r.File_type == "MP4" OR r.File_type == "MPEG" OR r.File_type == "WMV" OR r.File_type == "MOV"';
		}
		else{
			string request = request + 'AND (r.File_type == "AVI" OR r.File_type == "MP4" OR r.File_type == "MPEG" OR r.File_type == "WMV" OR r.File_type == "MOV")';
		}
	}

	if (scr_CB.isChhecked()){
		if (first){
			string request = request + 'r.File_type == "PNG" OR r.File_type == "JPG" OR r.File_type == "JPEG" OR r.File_type == "GIF" OR r.File_type == "BMP"';
		}
		if(vid_CB.isChecked()){
			string request = request + 'OR (r.File_type == "PNG" OR r.File_type == "JPG" OR r.File_type == "JPEG" OR r.File_type == "GIF" OR r.File_type == "BMP")';
		}
		else{
			string request = request + 'AND (r.File_type == "PNG" OR r.File_type == "JPG" OR r.File_type == "JPEG" OR r.File_type == "GIF" OR r.File_type == "BMP")';
		}
	}


	qDebug() << query.exec("SELECT rowid, * FROM Records");



	//qDebug() << query.exec("SELECT rowid, * FROM Records WHERE Camera");
	QSqlRecord rec = query.record();
	//QList<QString> headers;
	//QStringList headers;

	tableWidget.reset(new QTableWidget(this));
	tableWidget->setObjectName("tableWidget");
	ui.filter_VL->addWidget(tableWidget.get());

	tableWidget->setColumnCount(6); // Указываем число колонок
	tableWidget->setShowGrid(true); // Включаем сетку
	// Разрешаем выделение только одного элемента
	tableWidget->setSelectionMode(QAbstractItemView::SingleSelection);
	// Разрешаем выделение построчно
	tableWidget->setSelectionBehavior(QAbstractItemView::SelectRows);
	// Растягиваем последнюю колонку на всё доступное пространство
	tableWidget->horizontalHeader()->setStretchLastSection(true);
	// Скрываем колонку под номером 0
	tableWidget->hideColumn(0);
	// Устанавливаем заголовки колонок
	tableWidget->setHorizontalHeaderItem(0, new QTableWidgetItem("ID"));
	tableWidget->setHorizontalHeaderItem(1, new QTableWidgetItem("Record date"));
	tableWidget->setHorizontalHeaderItem(2, new QTableWidgetItem("OC number"));
	tableWidget->setHorizontalHeaderItem(3, new QTableWidgetItem("Camera"));
	tableWidget->setHorizontalHeaderItem(4, new QTableWidgetItem("File"));
	tableWidget->setHorizontalHeaderItem(5, new QTableWidgetItem(""));

	QString temp;
	for (int i = 0; query.next(); i++) {
		tableWidget->insertRow(i);
		tableWidget->setItem(i, 0, new QTableWidgetItem(query.value(0).toString()));
		tableWidget->setItem(i, 1, new QTableWidgetItem(query.value(1).toString()));
		tableWidget->setItem(i, 2, new QTableWidgetItem(query.value(2).toString()));
		switch (query.value(3).toInt())
		{
		case 1: temp = "Visible range wide angle"; break;
		case 2: temp = "Visible range narrow angle"; break;
		case 3: temp = "IR range narrow angle"; break;
		case 4: temp = "IR range narrow angle"; break;
		default: temp = "Error"; break;
		}
		tableWidget->setItem(i, 3, new QTableWidgetItem(temp));
		QWidget* temp_HLW = new QWidget(tableWidget.get());
		QHBoxLayout* temp_HL = new QHBoxLayout(temp_HLW);
		temp_HL->setContentsMargins(2, 2, 2, 2);
		temp_HLW->setLayout(temp_HL);
		File_PBs.push_back(new QPushButton("Open "+query.value(4).toString(), temp_HLW));
		temp_HL->addItem(new QSpacerItem(40, 20, QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Minimum));
		temp_HL->addWidget(File_PBs.back());
		temp_HL->addItem(new QSpacerItem(40, 20, QSizePolicy::Policy::Expanding, QSizePolicy::Policy::Minimum));
		File_PBs.back()->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
		//connect(File_PBs.back(), SIGNAL(clicked()), this, SLOT(slotReportBtnClicked()));
		tableWidget->setCellWidget(i, 4, temp_HLW);
		tableWidget->setCellWidget(i, 5, nullptr);
	}

	// Ресайзим колонки по содержимому
	tableWidget->resizeColumnsToContents();
	

	ui.filterL_L->setText("Filter");

	dateF_VLW.reset(new QWidget(this));
	dateF_VLW->setObjectName("dateF_VLW");
	dateF_VL.reset(new QVBoxLayout(dateF_VLW.get()));
	dateF_VL->setObjectName("dateF_VL");
	dateF_VLW->setLayout(dateF_VL.get());
	dateF_L.reset(new QLabel("Start date", this));
	dateF_L->setObjectName("dateF_L");
	dateF_VL->addWidget(dateF_L.get());
	dateF_DE.reset(new QDateEdit(this));
	dateF_DE->setObjectName("dateF_DE");
	dateF_VL->addWidget(dateF_DE.get());
	ui.ComboBox_HL->addWidget(dateF_VLW.get());

	dateL_VLW.reset(new QWidget(this));
	dateL_VLW->setObjectName("dateL_VLW");
	dateL_VL.reset(new QVBoxLayout(dateL_VLW.get()));
	dateL_VL->setObjectName("dateL_VL");
	dateL_VLW->setLayout(dateL_VL.get());
	dateL_L.reset(new QLabel("End date", this));
	dateL_L->setObjectName("dateL_L");
	dateL_VL->addWidget(dateL_L.get());
	dateL_DE.reset(new QDateEdit(this));
	dateL_DE->setObjectName("dateL_DE");
	dateL_VL->addWidget(dateL_DE.get());
	ui.ComboBox_HL->addWidget(dateL_VLW.get());

	OC_VLW.reset(new QWidget(this));
	OC_VLW->setObjectName("OC_VLW");
	OC_VL.reset(new QVBoxLayout(OC_VLW.get()));
	OC_VL->setObjectName("OC_VL");
	OC_VLW->setLayout(OC_VL.get());
	OC_L.reset(new QLabel("OC's number", this));
	OC_L->setObjectName("OC_L");
	OC_VL->addWidget(OC_L.get());
	OC_CombB.reset(new QComboBox(this));
	OC_CombB->setObjectName("OC_CombB");
	OC_CombB->addItem("All");
	for (size_t i = 0; i < SingletonOC::getInstance().getOCs().size(); i++)
		OC_CombB->addItem(QString("OC #%1").arg(i + 1));
	OC_VL->addWidget(OC_CombB.get());
	ui.ComboBox_HL->addWidget(OC_VLW.get());

	camVD1_CB.reset(new QCheckBox(this));
	camVD1_CB->setObjectName("camVD1_CB");
	camVD1_CB->setText("Visible range wide angle");
	ui.CB_GL->addWidget(camVD1_CB.get(), 0, 0);
	camVD2_CB.reset(new QCheckBox(this));
	camVD2_CB->setObjectName("camVD2_CB");
	camVD2_CB->setText("Visible range narrow angle");
	ui.CB_GL->addWidget(camVD2_CB.get(), 1, 0);
	camIK1_CB.reset(new QCheckBox(this));
	camIK1_CB->setObjectName("camIK1_CB");
	camIK1_CB->setText("IR range narrow angle");
	ui.CB_GL->addWidget(camIK1_CB.get(), 0, 1);
	camIK2_CB.reset(new QCheckBox(this));
	camIK2_CB->setObjectName("camIK2_CB");
	camIK2_CB->setText("IR range narrow angle");
	ui.CB_GL->addWidget(camIK2_CB.get(), 1, 1);
	vid_CB.reset(new QCheckBox(this));
	vid_CB->setObjectName("vid_CB");
	vid_CB->setText("Video");
	ui.CB_GL->addWidget(vid_CB.get(), 0, 2);
	scr_CB.reset(new QCheckBox(this));
	scr_CB->setObjectName("scr_CB");
	scr_CB->setText("Screenshot");
	ui.CB_GL->addWidget(scr_CB.get(), 1, 2);

	ui.accept_PB->setText("Accept");




}

ArchiveWindow::~ArchiveWindow() {}
