    def _create_status_bar(self):
        """Crea una barra de estado premium en la parte inferior."""
        from datetime import datetime
        
        # Crear widget de barra de estado
        status_bar = QtWidgets.QWidget()
        status_bar.setFixedHeight(32)
        status_bar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(15,23,42,0.98),
                    stop:0.5 rgba(30,41,59,0.95),
                    stop:1 rgba(15,23,42,0.98));
                border-top: 1px solid rgba(59,130,246,0.25);
            }
            QLabel {
                color: rgba(148,163,184,0.9);
                font-size: 11px;
                padding: 0 12px;
            }
        """)
        
        status_layout = QtWidgets.QHBoxLayout(status_bar)
        status_layout.setContentsMargins(12, 0, 12, 0)
        status_layout.setSpacing(16)
        
        # Información de la aplicación
        app_info = QtWidgets.QLabel("● Activo")
        app_info.setStyleSheet("QLabel { color: rgba(34,197,94,0.95); font-weight: 600; }")
        status_layout.addWidget(app_info)
        
        # Separador
        sep1 = QtWidgets.QLabel("|")
        sep1.setStyleSheet("QLabel { color: rgba(71,85,105,0.6); }")
        status_layout.addWidget(sep1)
        
        # Nombre de la app
        app_name = QtWidgets.QLabel("© 2026 GanaTodo")
        status_layout.addWidget(app_name)
        
        status_layout.addStretch(1)
        
        # Fecha y hora actual
        self.status_datetime = QtWidgets.QLabel()
        self._update_status_datetime()
        status_layout.addWidget(self.status_datetime)
        
        # Conectar timer
        if hasattr(self, '_timer'):
            self._timer.timeout.connect(self._update_status_datetime)
        
        # Agregar a la ventana principal
        central_layout = self.centralWidget().layout()
        central_layout.addWidget(status_bar)
    
    def _update_status_datetime(self):
        """Actualiza la fecha y hora en la barra de estado."""
        if not hasattr(self, 'status_datetime'):
            return
        from datetime import datetime
        now = datetime.now()
        self.status_datetime.setText(now.strftime("%d/%m/%Y  •  %I:%M:%S %p"))
