MAIN_WINDOW_STYLE = "QGroupBox {\n \
                        border: 1px solid grey;\n \
                        border-radius: 10px;\n \
                        margin-top: 7px;  /* <- Adds space for title to exist above border */\n \
                    }\n \
                    \n \
                    QGroupBox::title {  \n \
                        subcontrol-origin: margin;  /* <- Explicitly define or will be set to padding */\n \
                        subcontrol-position: top left;\n \
                        margin-left: 3px;\n \
                        margin-right: 3px;\n \
                        left: 5px;\n \
                    }"
GROUPBOX_STYLE = "QGroupBox {\n \
                        border: 1px solid grey;\n \
                        border-radius: 10px;\n \
                        margin-top: 7px;\n \
                        background-color: white;\n \
                    }\n \
                    \n \
                    QGroupBox::title {  \n \
                        color: black; \
                        subcontrol-origin: margin;\n \
                        subcontrol-position: top left;\n \
                        margin-left: 3px;\n \
                        margin-right: 3px;\n \
                        left: 5px;\n \
                    }"
                    
GROUPBOX_DISABLED_STYLE = "QGroupBox {\n \
                                border: 1px solid grey;\n \
                                border-radius: 10px;\n \
                                margin-top: 7px;\n \
                                background-color: white;\n \
                           }\n \
                            \n \
                            QGroupBox::title {  \n \
                                color: grey; \
                                subcontrol-origin: margin;\n \
                                subcontrol-position: top left;\n \
                                margin-left: 3px;\n \
                                margin-right: 3px;\n \
                                left: 5px;\n \
                            }"

PANEL_GROUPBOX_STYLE = "QGroupBox {\n \
                            border: 2px solid grey;\n \
                            border-radius: 10px;\n \
                            margin-top: 7px;\n \
                            background-color: white;\n \
                        }\n \
                        \n \
                        QGroupBox::title {  \n \
                            color: black; \
                            subcontrol-origin: margin;\n \
                            subcontrol-position: top left;\n \
                            margin-left: 3px;\n \
                            margin-right: 3px;\n \
                            left: 5px;\n \
                        }"

PANEL_GROUPBOX_DISABLED_STYLE = "QGroupBox {\n \
                                    color: grey; \
                                    border: 2px solid grey;\n \
                                    border-radius: 10px;\n \
                                    margin-top: 7px;\n \
                                    background-color: white;\n \
                                }\n \
                                \n \
                                QGroupBox::title {  \n \
                                    color: grey; \
                                    subcontrol-origin: margin;\n \
                                    subcontrol-position: top left;\n \
                                    margin-left: 3px;\n \
                                    margin-right: 3px;\n \
                                    left: 5px;\n \
                                }"

BUTTON_STYLE = "QPushButton {\n \
                    background-color: white;\n \
                    border-radius: 10px;\n \
                    padding: 5px;\n \
                    color: black;\n \
                    border: 1px solid grey\n \
                }\n \
                QPushButton:pressed {\n \
                    background-color: rgb(103, 204,209);\n \
                    border-style: inset;\n \
                }"
                
BUTTON_SELECTED_STYLE = "QPushButton {\n \
                            background-color: rgb(103, 204,209);\n \
                            border-radius: 10px;\n \
                            padding: 5px;\n \
                            color: black;\n \
                            border: 1px solid grey\n \
                        }\n \
                        QPushButton:pressed {\n \
                            background-color: rgb(103, 204,209);\n \
                            border-style: inset;\n \
                        }"

BUTTON_DISABLED_STYLE = "QPushButton {\n \
                            background-color: white;\n \
                            border-radius: 10px;\n \
                            padding: 5px;\n \
                            color: grey;\n \
                            border: 1px solid grey\n \
                        }\n"

BUTTON_MANUAL_STYLE = "QPushButton {\n \
                            background-color: white;\n \
                            border: none; \
                        }\n \
                        QPushButton:pressed {\n \
                            background-color: rgb(103, 204,209);\n \
                            border-style: inset;\n \
                        }"

MENU_BAR_STYLE =  "QMenuBar { \
                        background-color: #f0f0f0; \
                        border: 1px solid grey; \
                    } \
                   QMenuBar::item { \
                        background-color: transparent; \
                   } \
                   QMenuBar::item:selected { \
                        background-color: #a8a8a8; \
                   }"

MENU_STYLE = "QMenu::item { \
                background-color: transparent; \
              } \
              QMenu::item:selected { \
                background-color: #a8a8a8; \
              }"
              
NON_EDIT_TEXT_SYSTEM_STATE_STYLE = "border: none; color : rgb(0, 0, 255)"

EDIT_TEXT_BORDER_NON_STYLE = "border: none; background-color : white;"

NONEDIT_TEXT_LOG_STYLE = "border: 2px solid grey; border-radius: 10px;"

LABEL_CAMERA_STYLE = "background-color: black; color: white; border-radius: 10px"