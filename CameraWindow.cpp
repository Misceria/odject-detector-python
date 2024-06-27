/********************************************************************************
 * CameraWindow - Main window for camera viewer application.
 *
 * @file    CameraWindow.cpp
 * @author  Mr-Walrus <mr.walrus26@gmail.com>
 * @brief   This file contains the definition of the CameraWindow class, which
 *          represents the main window for the camera viewer application. It
 *          includes methods for displaying camera's frames, and handling user
 *			interactions.
 * @date    March 22, 2024
 * @license BSD
 ********************************************************************************/

#include "stdafx.h"
#include "CameraWindow.h"

CameraWindow::CameraWindow(QWidget* parent)
	: QMainWindow(parent), grid(new QGridLayout(this)), globalScrollArea(new QScrollArea(this)) {
	ui.setupUi(this);

	grid->setObjectName("grid");
	globalScrollArea->setObjectName("globalScrollArea");
	qDebug() << "#>\t CameraWindow() From thread: " << QThread::currentThreadId();

	camerasAmount = SingletonOC::getInstance().getOCs().size();
	globalScrollArea->setLayout(grid.get());
	size_t side = camerasAmount != 1 ? (camerasAmount / 2) : 1;
	for (int i = 0; i < camerasAmount; ++i) {
		frameViewers.append(QSharedPointer<FrameViewer>(new FrameViewer(i, this)));
		frameViewers.back()->setObjectName(QString("frameViewer#%1").arg(i + 1));
		frameViewers.back()->getImageLabel()->setBackgroundRole(QPalette::Base);
		frameViewers.back()->getImageLabel()->setSizePolicy(QSizePolicy::Ignored, QSizePolicy::Ignored);
		//	frameViewers.back()->getImageLabel()->setScaledContents(true);

		frameViewers.back()->getScrollArea()->setBackgroundRole(QPalette::Dark);
		frameViewers.back()->getScrollArea()->setWidget(frameViewers.back()->getImageLabel());
		grid->addWidget(frameViewers.back()->getScrollArea(), i / side, i % side);
		frameViewers.back()->getImageLabel()->adjustSize();
		frameViewers.back()->getScrollArea()->horizontalScrollBar()->setStyleSheet("QScrollBar {height:0px}");
		frameViewers.back()->getScrollArea()->verticalScrollBar()->setStyleSheet("QScrollBar {width:0px}");
		frameViewers.back()->getScrollArea()->setFrameShape(QFrame::Box);
		frameViewers.back()->getScrollArea()->setStyleSheet("QScrollArea {border: 0px solid black}");

		frameViewers.back()->getSectorLabel()->setText(QString("sector #%1 | zoom:").arg(i + 1));
		connect(frameViewers.back()->getRB1(), &QRadioButton::toggled, this, &CameraWindow::swapCameras);
		connect(frameViewers.back()->getRB4(), &QRadioButton::toggled, this, &CameraWindow::swapCameras);
		frameViewers.back()->getHLW()->setEnabled(false);
		//selectedFV = frameViewers.back().get();
		//QTimer::singleShot(100, this, [this]() {toggleVideoAnalytics(true); });
	}

	// QString msg = "";
	// statusBar()->showMessage(msg);

	sideBar.reset(new SideBar());
	sideBar->setObjectName("sideBar");
	// Добавьте боковое меню слева от главного виджета
	addDockWidget(Qt::LeftDockWidgetArea, sideBar.get());
	sideBar.get()->getBrightSlider()->setRange(0, 100 / adjustStep);
	sideBar.get()->getContrSlider()->setRange(0, 100 / adjustStep);
	sideBar.get()->getSaturSlider()->setRange(0, 100 / adjustStep);
	sideBar.get()->getSharpSlider()->setRange(0, 100 / adjustStep);

	connect(sideBar.get(), &SideBar::brightSliderValueChanged, this, &CameraWindow::adjustFrameBrightness);
	connect(sideBar.get(), &SideBar::contrSliderValueChanged, this, &CameraWindow::adjustFrameContrast);
	connect(sideBar.get(), &SideBar::saturSliderValueChanged, this, &CameraWindow::adjustFrameSaturation);
	connect(sideBar.get(), &SideBar::sharpSliderValueChanged, this, &CameraWindow::adjustFrameSharpness);

	connect(sideBar.get(), &SideBar::zoomSliderValueChanged, this, &CameraWindow::onZoomSliderValueChanged);
	connect(sideBar.get(), &SideBar::screenShotBTNClicked, this, &CameraWindow::saveCurrentFrame);
	connect(sideBar.get(), &SideBar::recordCBStateToggled, this, &CameraWindow::toggleVideoRecording);
	connect(sideBar.get(), &SideBar::audAnalytCBToggled, this, &CameraWindow::toggleAudioAnalytics);
	connect(sideBar.get(), &SideBar::vidAnalytCBToggled, this, &CameraWindow::toggleVideoAnalytics);
	connect(sideBar.get(), &SideBar::autoZoomCBToggled, this, &CameraWindow::toggleAutoZoom);

	connect(sideBar.get(), &SideBar::controlBTNClicked, this, &CameraWindow::onControlBTNClicked);
	connect(sideBar.get(), &SideBar::controlBTNPressed, this, &CameraWindow::onControlBTNPressed);
	connect(sideBar.get(), &SideBar::controlBTNReleased, this, &CameraWindow::onControlBTNReleased);


	setCentralWidget(globalScrollArea.get());

	createActions();

	//move(0, 0);
	resize(QGuiApplication::primaryScreen()->availableSize() * 4 / 5);
	//setWindowState(Qt::WindowFullScreen);

	globalScrollArea->setVisible(true);

	//initializeCameras();
	//updateCameraFrames();

	SingletonOC::getInstance().addRadarObserver(this);

	connect(this, &CameraWindow::updCam, this, &CameraWindow::onUpdCam);
	QTimer::singleShot(10, this, &CameraWindow::initializeCameras);
	//QString fileName = QFileDialog::getSaveFileName(this, tr("Save Frame"), QDir::currentPath(), tr("Image Files (*.png *.jpg *.bmp)"));
}

FrameViewer* CameraWindow::getSelectedFV() {
	for (int i = 0; i < camerasAmount; i++) {
		if (frameViewers[i]->getImageLabel() == selectedWidget ||
			frameViewers[i]->getScrollArea() == selectedWidget ||
			frameViewers[i]->getHLW() == selectedWidget ||
			frameViewers[i]->getRB1() == selectedWidget ||
			frameViewers[i]->getRB4() == selectedWidget ||
			frameViewers[i]->getSectorLabel() == selectedWidget) {
			selectedFV = frameViewers[i].get();
			return selectedFV;
		}
	}
	return nullptr;
}

void CameraWindow::initializeCameras() {
	for (int i = 0; i < camerasAmount; ++i) {
		//SingletonOC::getInstance().getOCs().at(i)->getCams()->lastCam().connect();
		OCsptr.emplace_back(SingletonOC::getInstance().getOCs().at(i).get());
		OCsptr[i]->getCams()->lastCam().connect();
		//SingletonOC::getInstance().getOCs().at(i)->getCams()->lastCam().getFrame(*frameViewers[i]->getCurFrameSrc());
		frameViewers[i]->setX4FrameScale(OCsptr[i]->getCams()->x4().getHorFov() / OCsptr[i]->getCams()->x1().getHorFov());
		//frameViewers[i]->setX4FrameScale(0.48); // stat
		//frameViewers[i]->setX4FrameScale(0.27); // 10
		//frameViewers[i]->setX4FrameScale(0.58); // 22
		frameViewers[i]->setX4CamSize(OCsptr[i]->getCams()->x4().getFrameSize());
		frameViewers[i]->setX1CamSize(OCsptr[i]->getCams()->x1().getFrameSize());
		OCsptr[i]->getCams()->lastCam().getGPUFrame(*frameViewers[i]->getCurGPUFrameSrc());
		frameViewers[i]->setImage();

		//QLabel* sectorLabel = frameViewers[i]->getSectorLabel();
		QWidget* OHLW = frameViewers[i]->getOHLW();
		//sectorLabel->move(10, 10);
		//OHLW->move(sectorLabel->width() + 10 - OHLW->width() - 5, 10 + (sectorLabel->height() - OHLW->height()) / 2);
		OHLW->move(10, 10);
		//frameViewers[i]->getScrollArea()->setStyleSheet("QScrollArea {border: 0px solid black}");
		frameViewers[i]->setAudAnalyt(frameViewers[i]->usesAudAnalyt());
	}
	for (int i = 0; i < camerasAmount; ++i)
		frameViewers[i]->fitToWindow();
	QTimer::singleShot(10, this, &CameraWindow::updateCameraFrames);
}

template <class T>
T navr(T newNumber) {
	const int n = 30; // количество последних чисел для усреднения
	static T sum = 0, recentNumbers[n] = { 0 }; // массив для хранения последних n чисел
	static int count = 0, index = 0;

	sum -= recentNumbers[index];
	recentNumbers[index] = newNumber;
	sum += newNumber;
	count = (count < n) ? count + 1 : n; // Обновляем количество чисел в сумме
	index = (index + 1) % n; // Обновляем индекс для нового числа

	return sum / count;
}

void CameraWindow::updateCameraFrames() {
	auto start = std::chrono::steady_clock::now();
	for (int i = 0; i < camerasAmount; ++i)
		emit updCam(i);
	auto end = std::chrono::steady_clock::now();
	auto duration = std::max(std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count(), 1ll);
	QString msg = QString("Exec time: %1 fps").arg(1000 / duration) + QString(" | avr: %2").arg(navr(1000 / duration));
	statusBar()->showMessage(msg);
	QTimer::singleShot(1000 / 1000, this, &CameraWindow::updateCameraFrames);
}

void CameraWindow::onUpdCam(int index)
{
	OCsptr[index]->getCams()->lastCam().getGPUFrame(*frameViewers[index]->getCurGPUFrameSrc());
	std::vector<cv::Rect> targetRects;
	bool haveNewRect = false;
	double conf;
	haveNewRect = OCsptr[index]->getTargetRects(targetRects, conf);
	frameViewers[index]->adjustFrameProperties(haveNewRect, targetRects, conf);
	//frameViewers[index]->updateImage();
}

void CameraWindow::updateSideBar() {
	if (selectedFV) {
		sideBar->getZoomSlider()->setMinimum(0);
		sideBar->getZoomSlider()->setMaximum(int(selectedFV->getScale() * 2.));
		sideBar->getZoomSlider()->setValue(selectedFV->getCurScaleStep() + selectedFV->getScale());
		sideBar->getZoomSlider()->setSingleStep(1);
		sideBar->getRecordCB()->setChecked(selectedFV->isRecording());


		sideBar->getBrightSlider()->setValue(selectedFV->getBrightness() / adjustStep);
		sideBar->getContrSlider()->setValue(selectedFV->getContrast() / adjustStep);
		sideBar->getSaturSlider()->setValue(selectedFV->getSaturation() / adjustStep);
		sideBar->getSharpSlider()->setValue(selectedFV->getSharpness() / adjustStep);

		sideBar->getAudAnalytCB()->setChecked(selectedFV->usesAudAnalyt());
		sideBar->getVidAnalytCB()->setChecked(selectedFV->usesVidAnalyt());
		sideBar->getAutoZoomCB()->setChecked(selectedFV->usesAutoZoom());
	}
}

void CameraWindow::onControlBTNClicked(int index) {
	//statusBar()->showMessage("Clicked " + QString::number(index));
	static const cv::Point2d ang[9] = {
		cv::Point2d(-5, 5),  cv::Point2d(0, 5),   cv::Point2d(5, 5),
		cv::Point2d(-5, 0),  cv::Point2d(0, 0),   cv::Point2d(5, 0),
		cv::Point2d(-5, -5), cv::Point2d(0, -5),  cv::Point2d(5, -5) };
	if (selectedFV) {
		if (index == 4)
			SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getOPU()->diagnoseOPU();
		//else
		//	SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getOPU()->rotateOPUonDelta(ang[index]);
	}
}

void CameraWindow::onControlBTNPressed(int index) {
	//statusBar()->showMessage("Pressed " + QString::number(index));
	static const cv::Point2d ang[9] = {
		cv::Point2d(-20, 20),  cv::Point2d(0, 20),   cv::Point2d(20, 20),
		cv::Point2d(-20, 0),   cv::Point2d(0, 0),    cv::Point2d(20, 0),
		cv::Point2d(-20, -20), cv::Point2d(0, -20),  cv::Point2d(20, -20) };
	if (selectedFV && index != 4)
		SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getOPU()->rotateOPUwithSpeed(ang[index]);
}

void CameraWindow::onControlBTNReleased(int index) {
	//statusBar()->showMessage("Released " + QString::number(index));
	if (selectedFV && index != 4)
		SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getOPU()->rotateOPUwithSpeed(cv::Point2d(0, 0));
}

void CameraWindow::adjustFrameBrightness(int value) {
	if (selectedFV && selectedFV->getBrightness() != value * adjustStep)
		selectedFV->setBrightness(value * adjustStep);
}
void CameraWindow::adjustFrameContrast(int value) {
	if (selectedFV && selectedFV->getContrast() != value * adjustStep)
		selectedFV->setContrast(value * adjustStep);
}
void CameraWindow::adjustFrameSaturation(int value) {
	if (selectedFV && selectedFV->getSaturation() != value * adjustStep)
		selectedFV->setSaturation(value * adjustStep);
}
void CameraWindow::adjustFrameSharpness(int value) {
	if (selectedFV && selectedFV->getSharpness() != value * adjustStep)
		selectedFV->setSharpness(value * adjustStep);
}

std::string toStdString(QString qstr) {
	std::string temp;
	for (size_t i = 0; i < qstr.length(); i++)
		temp.push_back(qstr[i].toLatin1());
	return temp;	
}

void CameraWindow::saveCurrentFrame() {
	if (selectedFV) {
		if (!selectedFV->getCurFrame().empty()) {
			QString fileName = QDateTime::currentDateTime().toString("yyyyMMdd_hhmmss") + "_camera" + QString::number(selectedFV->getCamNum() + 1) + ".png";
			QString filePath = basePath + QDir::separator() + fileName;
			cv::Mat frame;
			//cv::cvtColor(selectedFV->getCurFrame(), frame, cv::COLOR_RGB2BGR);
			cv::imwrite(toStdString(filePath), selectedFV->getCurFrame());
			statusBar()->showMessage("Frame saved successfully");
		}
		else {
			statusBar()->showMessage("Failed to capture frame");
		}
	}
	else {
		statusBar()->showMessage("No frame viewer selected");
	}
}

void CameraWindow::toggleVideoRecording(bool checked) {
	if (selectedFV && selectedFV->isRecording() != checked) {
		selectedFV->setRecording(checked);
		QString fileName = QDateTime::currentDateTime().toString("yyyyMMdd_hhmmss") + "_camera" + QString::number(selectedFV->getCamNum() + 1);
		QString filePath = basePath + QDir::separator() + fileName + "x4.avi";
		int resx4 = SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getCams()->x4().setRecording(checked, toStdString(filePath));

		filePath = basePath + QDir::separator() + fileName + "x1.avi";
		int resx1 = SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getCams()->x1().setRecording(checked, toStdString(filePath));

		if (resx4 == 0)
			statusBar()->showMessage("Failed to open video file for writing cam x4");
		if (resx1 == 0)
			statusBar()->showMessage("Failed to open video file for writing cam x1");
		if (resx4 == 1 && resx1 == 1)
			statusBar()->showMessage("Video recording started: " + filePath);
		else if (resx4 == 2 && resx1 == 2)
			statusBar()->showMessage("Video recording stopped");
	}
	else {
		statusBar()->showMessage("No frame viewer selected");
	}
}

void CameraWindow::toggleAudioAnalytics(bool checked) {
	if (selectedFV && selectedFV->usesAudAnalyt() != checked) {
		selectedFV->setAudAnalyt(checked);
	}
	else {
		statusBar()->showMessage("No frame viewer selected");
	}
}

void CameraWindow::toggleVideoAnalytics(bool checked) {
	if (selectedFV && selectedFV->usesVidAnalyt() != checked) {
		selectedFV->setVidAnalyt(checked);
		SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->setNNEnabled(checked);
	}
	else {
		statusBar()->showMessage("No frame viewer selected");
	}
}

void CameraWindow::toggleAutoZoom(bool checked) {
	if (selectedFV && selectedFV->usesAutoZoom() != checked) {
		selectedFV->setAutoZoom(checked);
	}
	else {
		statusBar()->showMessage("No frame viewer selected");
	}
}

void CameraWindow::onZoomSliderValueChanged(int value) {
	if (selectedFV) {
		value -= selectedFV->getScale();
		if (selectedFV->getCurScaleStep() != value)
			selectedFV->zoomToStep(value);
	}
}

void CameraWindow::toggleSideBar() {
	// Переключайте видимость бокового меню
	sideBar->setVisible(!sideBar->isVisible());
}
void CameraWindow::toggleSwing() {
	if (selectedFV )
		SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getOPU()->sendReceive("$k,300,60,15#");
}

void CameraWindow::camWarning(size_t camNum) {
	static bool test = false;
	if (frameViewers[camNum] && !frameViewers[camNum]->isWarningToggled()) {
		test = !test;
		frameViewers[camNum]->setAudWarn(test);
		frameViewers[camNum]->setWarningToggled(true);
		frameViewers[camNum]->getScrollArea()->setStyleSheet("QScrollArea {border: 5px solid rgb(220,20,60)}");
		statusBar()->showMessage(QString("cam #%1 detect target").arg(camNum + 1));
		statusBar()->setStyleSheet("QStatusBar {background: rgb(220,20,60)}");
	}
}

void CameraWindow::updateData(size_t serialNum, size_t targetId, cv::Point3d tempCort) {
	camWarning(serialNum);
}

void CameraWindow::mousePressEvent(QMouseEvent* event) {
	selectedWidget = childAt(event->pos());
	FrameViewer* privSelectedFV = selectedFV;
	if (getSelectedFV() && privSelectedFV != selectedFV) {
		if (privSelectedFV) {
			privSelectedFV->getScrollArea()->setStyleSheet("QScrollArea {border: 0px solid black}");
			privSelectedFV->getHLW()->setEnabled(false);
			//QLabel* sectorLabel = privSelectedFV->getSectorLabel();
			//QWidget* HLW = privSelectedFV->getHLW();
			//sectorLabel->move(10, 10);
			//HLW->move(sectorLabel->width() + 10 - HLW->width() - 5, 10 + (sectorLabel->height() - HLW->height()) / 2);
		}
		selectedFV->getScrollArea()->setStyleSheet("QScrollArea {border: 2px solid cyan}");
		selectedFV->getHLW()->setEnabled(true);
		/*QLabel* sectorLabel = selectedFV->getSectorLabel();
		QWidget* HLW = selectedFV->getHLW();
		sectorLabel->move(10, 10);
		HLW->move(sectorLabel->width() + 10 - HLW->width() - 5, 10 + (sectorLabel->height() - HLW->height()) / 2);*/
		updateSideBar();
	}
	//statusBar()->showMessage(selectedWidget->objectName());
	//statusBar()->setStyleSheet("QStatusBar {background: red}");
}

void CameraWindow::mouseDoubleClickEvent(QMouseEvent* event) {
	//	selectedWidget = childAt(event->pos());
	if (getSelectedFV()) {
		fullScreenAct->setChecked(!fullScreenAct->isChecked());
		QTimer::singleShot(10, this, &CameraWindow::fitToWindow);
	}
	fullScreen();
}


void CameraWindow::wheelEvent(QWheelEvent* event) {
	if (event->angleDelta().y() > 0) zoomOut();
	else zoomIn();
	updateSideBar();
}



void CameraWindow::zoomIn() {
	if (selectedFV) selectedFV->zoomIn();
	updateSideBar();
}

void CameraWindow::zoomOut() {
	if (selectedFV) selectedFV->zoomOut();
	updateSideBar();
}

void CameraWindow::normalSize() {
	if (selectedFV) selectedFV->normalSize();
	updateSideBar();
}

void CameraWindow::fitToWindow() {
	if (selectedFV) selectedFV->fitToWindow();
	updateSideBar();
}

void CameraWindow::fullScreen() {
	static QRect oldGeometry;
	if (fullScreenAct->isChecked() && getSelectedFV()) {
		oldGeometry = selectedFV->getScrollArea()->geometry();
		QRect newGeometry;
		newGeometry.setWidth(this->size().width()); // Подгоняем под размер окна
		newGeometry.setHeight(this->size().height() - statusBar()->size().height() - menuBar()->size().height());
		selectedFV->getScrollArea()->setGeometry(newGeometry);
		selectedFV->getScrollArea()->raise(); // Перемещаем выбранный виджет на верхний уровень стека окон
	}
	else if (getSelectedFV())
		selectedFV->getScrollArea()->setGeometry(oldGeometry);
	else
		fullScreenAct->setChecked(!fullScreenAct->isChecked());
}

void CameraWindow::swapCameras()
{
	if (selectedFV->getRB1()->isChecked() && selectedFV) {
		SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getCams()->x1().connect();
		QTimer::singleShot(10, this, &CameraWindow::fitToWindow);
	}
	else if (selectedFV->getRB4()->isChecked() && selectedFV) {
		SingletonOC::getInstance().getOCs().at(selectedFV->getCamNum())->getCams()->x4().connect();
		QTimer::singleShot(10, this, &CameraWindow::fitToWindow);
	}
	updateSideBar();
}

void CameraWindow::toggleCamWarning() {
	if (selectedFV)
		if (selectedFV->isWarningToggled()) {
			selectedFV->setWarningToggled(false);
			selectedFV->getScrollArea()->setStyleSheet("QScrollArea {border: 2px solid cyan}");
			statusBar()->setStyleSheet("QStatusBar {background: auto}");
		}
		else
			camWarning(selectedFV->getCamNum());
}

void CameraWindow::createActions() {

	QMenu* logoMenu = menuBar()->addMenu(QIcon("SpiderSpyW.ico"), tr("&Logo"));
	logoMenu->setEnabled(false);

	QMenu* fileMenu = menuBar()->addMenu(tr("&File"));

	fileMenu->addSeparator();

	QAction* toolsAct = fileMenu->addAction(tr("&Tools"), this, &CameraWindow::toggleSideBar);
	toolsAct->setShortcut(tr("Ctrl+T"));

	QAction* exitAct = fileMenu->addAction(tr("E&xit"), this, &QWidget::close);
	exitAct->setShortcut(tr("Ctrl+Q"));

	QAction* swingAct = fileMenu->addAction(tr("S&wing"), this, &CameraWindow::toggleSwing);
	swingAct->setShortcut(tr("Ctrl+S"));

	QMenu* viewMenu = menuBar()->addMenu(tr("&View"));

	zoomInAct = viewMenu->addAction(tr("Zoom &In (25%)"), this, &CameraWindow::zoomIn);
	zoomInAct->setShortcut(QKeySequence::ZoomIn);
	zoomInAct->setEnabled(true);

	zoomOutAct = viewMenu->addAction(tr("Zoom &Out (25%)"), this, &CameraWindow::zoomOut);
	zoomOutAct->setShortcut(QKeySequence::ZoomOut);
	zoomOutAct->setEnabled(true);

	normalSizeAct = viewMenu->addAction(tr("&Normal Size"), this, &CameraWindow::normalSize);
	normalSizeAct->setShortcut(tr("Ctrl+N"));
	normalSizeAct->setEnabled(true);

	fitToWindowAct = viewMenu->addAction(tr("&Fit to Window"), this, &CameraWindow::fitToWindow);
	fitToWindowAct->setShortcut(tr("Ctrl+F"));
	fitToWindowAct->setEnabled(true);

	fullScreenAct = viewMenu->addAction(tr("F&ull Screen"), this, &CameraWindow::fullScreen);
	fullScreenAct->setShortcut(tr("Ctrl+U"));
	fullScreenAct->setEnabled(true);
	fullScreenAct->setCheckable(true);

	QAction* warningAct = viewMenu->addAction(tr("&Warning"), this, &CameraWindow::toggleCamWarning);
	warningAct->setShortcut(tr("Ctrl+W"));
	warningAct->setEnabled(true);

	menuBar()->raise();
}
