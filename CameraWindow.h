/********************************************************************************
 * CameraWindow - Main window for camera viewer application.
 *
 * @file    CameraWindow.h
 * @author  Mr-Walrus <mr.walrus26@gmail.com>
 * @brief   This file contains the definition of the CameraWindow class, which
 *          represents the main window for the camera viewer application. It
 *          includes methods for displaying camera's frames, and handling user
 *			interactions.
 * @date    March 22, 2024
 * @license BSD
 ********************************************************************************/

#pragma once

#include <QMainWindow>
#include "ui_CameraWindow.h"
#include "ObservComplex.h"
#include "Radar.h"
#include "FrameViewer.h"
#include "SideBar.h"

 /** @brief Window class for the camera application.
 This class represents the window of the camera application. It contains
 widgets for displaying camera frames, controlling settings, and managing sidebars.

 It includes slots for handling user actions and private helper methods for managing
 the window state and interactions.
 */
class CameraWindow : public QMainWindow, Observer
{
	Q_OBJECT

public:
	/** @brief Constructor for CameraWindow.
	@param parent Pointer to the parent widget.
	*/
	CameraWindow(QWidget* parent = nullptr);

signals:
	void updCam(int index);

public slots:

	void onControlBTNClicked(int index);
	void onControlBTNPressed(int index);
	void onControlBTNReleased(int index);

	/** @brief Slot to adjust current frame Brightness.
	@param value New value of the slider.
	*/
	void adjustFrameBrightness(int value);

	/** @brief Slot to adjust current frame Contrast.
	@param value New value of the slider.
	*/
	void adjustFrameContrast(int value);

	/** @brief Slot to adjust current frame Saturation.
	@param value New value of the slider.
	*/
	void adjustFrameSaturation(int value);

	/** @brief Slot to adjust current frame Sharpness.
	@param value New value of the slider.
	*/
	void adjustFrameSharpness(int value);

	/** @brief Slot to save the current frame. */
	void saveCurrentFrame();

	/** @brief Slot to toggle video recording.
	@param state State of the recording toggle.
	*/
	void toggleVideoRecording(bool checked);

	/** @brief Slot to toggle audio analytics.
	@param state State of the analytics toggle.
	*/
	void toggleAudioAnalytics(bool checked);

	/** @brief Slot to toggle video analytics.
	@param state State of the analytics toggle.
	*/
	void toggleVideoAnalytics(bool checked);

	/** @brief Slot to toggle video analytics.
	@param state State of the analytics toggle.
	*/
	void toggleAutoZoom(bool checked);

	/** @brief Slot to handle zoom slider value changes.
	@param value New value of the zoom slider.
	*/
	void onZoomSliderValueChanged(int value);

	/** @brief Slot to toggle the visibility of the sidebar. */
	void toggleSideBar();

	void toggleSwing();

	/** @brief Slot to handle camera warnings.
	@param camNum Index of the camera.
	*/
	void camWarning(size_t camNum);

private slots:
	/** @brief Slot to zoom in on the selected frame viewer. */
	void zoomIn();

	/** @brief Slot to zoom out on the selected frame viewer. */
	void zoomOut();

	/** @brief Slot to restore the selected frame viewer to its normal size. */
	void normalSize();

	/** @brief Slot to fit the selected frame viewer to the window. */
	void fitToWindow();

	/** @brief Slot to toggle fullscreen mode. */
	void fullScreen();

	/** @brief Slot to swap between different cameras. */
	void swapCameras();

	/** @brief Slot to toggle camera warnings. */
	void toggleCamWarning();


	void onUpdCam(int index);

	//void openSettings();


private:
	size_t camerasAmount = 0; // Number of cameras connected
	std::vector<ObservComplex*> OCsptr;
	bool fullscreen = false; // Flag indicating fullscreen mode
	double scale = 8; // The max scale for frame viewers.
	double zoomInFactor = 1.25; // The zoom In factor for frame viewers.
	double zoomOutFactor = 0.8; // The zoom Out factor for frame viewers.
	double normalScaleFactor = 1.; // The scale factor for frame viewers.
	double maxScaleFactor = normalScaleFactor * pow(zoomInFactor, scale); // Max scaling factor for frame viewers.
	double minScaleFactor = normalScaleFactor * pow(zoomOutFactor, scale); // Min scaling factor for frame viewers.
	QString basePath = "./DB"; // Base path for storing data.
	int adjustStep = 10;

	void updateData(size_t serialNum, size_t targetId, cv::Point3d tempCort) override;

	/** @brief Overridden mouse press event handler for selecting FrameViewer widget. */
	void mousePressEvent(QMouseEvent* event) override;

	/** @brief Overridden mouse double click event handler for toggling fullscreen mode. */
	void mouseDoubleClickEvent(QMouseEvent* event);

	/** @brief Overridden wheel event handler for zooming. */
	void wheelEvent(QWheelEvent* event);

	/** @brief Update camera frames displayed in the window. */
	void updateCameraFrames();

	/** @brief Update sidebar widget content. */
	void updateSideBar();

	//void keyPressEvent(QKeyEvent* event);

	/** @brief Create actions for menu. */
	void createActions();

	/** @brief Get the selected FrameViewer widget.
	@return Pointer to the selected FrameViewer widget.
	*/
	FrameViewer* getSelectedFV();

	/** @brief Initialize cameras and associated widgets. */
	void initializeCameras();

	FrameViewer* selectedFV = nullptr; // Pointer to the selected FrameViewer
	QWidget* selectedWidget = nullptr; // Pointer to the selected widget

	QScopedPointer<SideBar> sideBar; // Pointer to the sidebar widget
	QScopedPointer<QGridLayout> grid; // Layout for arranging widgets
	QScopedPointer<QScrollArea> globalScrollArea; // Scroll area for the entire window
	QVector<QSharedPointer<FrameViewer>> frameViewers; // Vector of FrameViewer widgets

	QAction* printAct; // Action for printing
	QAction* zoomInAct; // Action for zooming in
	QAction* zoomOutAct; // Action for zooming out
	QAction* normalSizeAct; // Action for restoring normal size
	QAction* fitToWindowAct; // Action for fitting to window
	QAction* fullScreenAct; // Action for toggling fullscreen mode

	Ui::CameraWindowClass ui; // UI object
};
