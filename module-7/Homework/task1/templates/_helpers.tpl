{{- define "host" -}}
  {{- if eq .Values.global.env "test" }}
    {{- default .Values.host.test }}
  {{- else if eq .Values.global.env "prod" }}
    {{- default .Values.host.prod }}
  {{- else }}
    {{- default .Values.host._default }}
  {{- end }}
{{- end }}