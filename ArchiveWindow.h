/********************************************************************************
 * ArchiveWindow - Main window for archive viewer application.
 *
 * @file    ArchiveWindow.h
 * @author  Mr-Walrus <mr.walrus26@gmail.com>
 * @brief   This file contains the declaration of the ArchiveWindow class, which
 *          represents the main window for the archive viewer application. It
 *          provides functionality for viewing archived data and managing user
 *          interactions.
 * @date    March 14, 2024
 * @license BSD
 ********************************************************************************/

#pragma once

#include <QMainWindow>
#include <QtSql/QSql>
#include <QtSql/QSqlDatabase>
#include <QtSql/QSqlQuery>
#include <QtSql/QSqlRecord>
#include <QtSql/QSqlTableModel>
#include "ObservComplex.h"
#include "ui_ArchiveWindow.h"

class ArchiveWindow : public QMainWindow
{
	Q_OBJECT

public:
	ArchiveWindow(QWidget *parent = nullptr);
	~ArchiveWindow();

private:

	QScopedPointer<QWidget> dateF_VLW;
	QScopedPointer<QLabel> dateF_L;
	QScopedPointer<QVBoxLayout> dateF_VL;
	QScopedPointer<QDateEdit> dateF_DE;

	QScopedPointer<QWidget> dateL_VLW;
	QScopedPointer<QLabel> dateL_L;
	QScopedPointer<QVBoxLayout> dateL_VL;
	QScopedPointer<QDateEdit> dateL_DE;

	QScopedPointer<QWidget> OC_VLW;
	QScopedPointer<QLabel> OC_L;
	QScopedPointer<QVBoxLayout> OC_VL;
	QScopedPointer<QComboBox> OC_CombB;

	QScopedPointer<QCheckBox> camVD1_CB;
	QScopedPointer<QCheckBox> camVD2_CB;
	QScopedPointer<QCheckBox> camIK1_CB;
	QScopedPointer<QCheckBox> camIK2_CB;
	QScopedPointer<QCheckBox> vid_CB;
	QScopedPointer<QCheckBox> scr_CB;

	QScopedPointer<QTableWidget> tableWidget;
	QVector<QPushButton*> File_PBs;

	Ui::ArchiveWindowClass ui;
};
