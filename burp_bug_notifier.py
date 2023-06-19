from this import d
from burp import IBurpExtender
from burp import ITab
from java.io import PrintWriter
from burp import IProxyListener
from threading import Thread
from burp import IHttpListener
from burp import IMessageEditorController
from burp import IScanIssue
from java.awt import Component;
from java.io import PrintWriter;
from java.util import ArrayList;
from java.util import List;
from javax.swing import JScrollPane;
from javax.swing import JSplitPane;
from javax.swing import JTabbedPane;
from javax.swing import JTable;
from javax.swing import SwingUtilities;
from javax.swing.table import AbstractTableModel;
from javax.swing import JButton
from java.awt.event import ActionListener

from threading import Lock
import base64
import re
import threading


import urllib

XSS_payload = '1" onmouseover=alert(97912) "'
ERROR_MSG = "KFtBLVphLXpdezEsMzJ9XC4pK1tBLVphLXpdezAsMzJ9XCgoW0EtWmEtejAtOV0rXHMrW0EtWmEtejAtOV0rWyxcc10qKSpcKVxzK1wrezF9XGQrCUFTUC5OZXQJQ2VydGFpbglIaWdoCiJNZXNzYWdlIjoiSW52YWxpZCB3ZWIgc2VydmljZSBjYWxsCUFTUC5OZXQJQ2VydGFpbglIaWdoCkV4Y2VwdGlvbiBvZiB0eXBlCUFTUC5OZXQJQ2VydGFpbglIaWdoCi0tLSBFbmQgb2YgaW5uZXIgZXhjZXB0aW9uIHN0YWNrIHRyYWNlIC0tLQlBU1AuTmV0CUNlcnRhaW4JSGlnaApNaWNyb3NvZnQgT0xFIERCIFByb3ZpZGVyCUFTUC5OZXQJQ2VydGFpbglIaWdoCkVycm9yIChbXGQtXSspIFwoW1xkQS1GYS1mXStcKQlBU1AuTmV0CUNlcnRhaW4JSGlnaApcYmF0IChbYS16QS1aMC05X10qXC4pKihbYS16QS1aMC05X10rKVwoW2EtekEtWjAtOSwgXFtcXVwmXDtdKlwpCUFTUC5OZXQJQ2VydGFpbiAzCUhpZ2gKKFtBLVphLXpdezEsMzJ9XC4pK1tBLVphLXpdezAsMzJ9RXhjZXB0aW9uOglBU1AuTmV0CUNlcnRhaW4gMglIaWdoCmluIFtBLVphLXpdOlxcKFtBLVphLXowLTlfXStcXCkrW0EtWmEtejAtOV9cLV0rKFwuYXNweCk/XC5jczpsaW5lIFtcZF0rCUFTUC5OZXQJQ2VydGFpbglIaWdoClN5bnRheCBlcnJvciBpbiBzdHJpbmcgaW4gcXVlcnkgZXhwcmVzc2lvbglBU1AuTmV0CUNlcnRhaW4JSGlnaApcLmphdmE6WzAtOV0rCUphdmEJQ2VydGFpbglIaWdoClwuamF2YVwoKElubGluZWQgKT9Db21waWxlZCBDb2RlXCkJSmF2YQlDZXJ0YWluCUhpZ2gKXC5pbnZva2VcKFVua25vd24gU291cmNlXCkJSmF2YQlDZXJ0YWluCUhpZ2gKbmVzdGVkIGV4Y2VwdGlvbiBpcwlKYXZhCUZpcm0JSGlnaApcLmpzOlswLTldKzpbMC05XSsJSmF2YXNjcmlwdAlDZXJ0YWluCUhpZ2gKSkJXRUJbMC05XXs2fToJSkJvc3MJRmlybQlIaWdoCigoZG58ZGN8Y258b3V8dWlkfG98Yyk9W1x3XGRdKixccz8pezIsfQlMREFQCUZpcm0JSGlnaApcWyhPREJDIFNRTCBTZXJ2ZXIgRHJpdmVyfFNRTCBTZXJ2ZXJ8T0RCQyBEcml2ZXIgTWFuYWdlcilcXQlNaWNyb3NvZnQgU1FMIFNlcnZlcglDZXJ0YWluCUhpZ2gKQ2Fubm90IGluaXRpYWxpemUgdGhlIGRhdGEgc291cmNlIG9iamVjdCBvZiBPTEUgREIgcHJvdmlkZXIgIltcd10qIiBmb3IgbGlua2VkIHNlcnZlciAiW1x3XSoiCU1pY3Jvc29mdCBTUUwgU2VydmVyCUNlcnRhaW4JSGlnaApZb3UgaGF2ZSBhbiBlcnJvciBpbiB5b3VyIFtBLVphLXpdKyBzeW50YXg7IGNoZWNrIHRoZSBtYW51YWwgdGhhdCBjb3JyZXNwb25kcwlNeVNRTAlDZXJ0YWluCUhpZ2gKSWxsZWdhbCBtaXggb2YgY29sbGF0aW9ucyBcKFtcd1xzXCxdK1wpIGFuZCBcKFtcd1xzXCxdK1wpIGZvciBvcGVyYXRpb24JTXlTUUwJQ2VydGFpbglIaWdoCmF0IChcL1tBLVphLXowLTlcLl0rKSpcLnBtIGxpbmUgWzAtOV0rCVBlcmwJQ2VydGFpbglNZWRpdW0KXC5waHAgb24gbGluZSBbMC05XSsJUEhQCUNlcnRhaW4JTWVkaXVtClwucGhwPC9iPiBvbiBsaW5lIDxiPlswLTldKwlQSFAJQ2VydGFpbglNZWRpdW0KRmF0YWwgZXJyb3IJRkFUQUwJQ2VydGFpbglNZWRpdW0KXC5waHA6WzAtOV0rCVBIUAlDZXJ0YWluCU1lZGl1bQpUcmFjZWJhY2sgXChtb3N0IHJlY2VudCBjYWxsIGxhc3RcKToJUHl0aG9uCUNlcnRhaW4JSGlnaApcWyhPREJDIFNRTCBTZXJ2ZXIgRHJpdmVyfFNRTCBTZXJ2ZXJ8T0RCQyBEcml2ZXIgTWFuYWdlcilcXQlNaWNyb3NvZnQgU1FMIFNlcnZlcglDZXJ0YWluCUhpZ2gKXC5qYXZhOlswLTldKwlKYXZhCUNlcnRhaW4JSGlnaApcLmphdmFcKChJbmxpbmVkICk/Q29tcGlsZWQgQ29kZVwpCUphdmEJQ2VydGFpbglIaWdoCltBLVphLXpcLl0rXCgoW0EtWmEtejAtOSwgXSspP1wpIFwrWzAtOV0rCUFTUC5OZXQJQ2VydGFpbglIaWdoCmF0IChcL1tBLVphLXowLTlcLl0rKSpcLnBtIGxpbmUgWzAtOV0rCVBlcmwJQ2VydGFpbglIaWdoCkZpbGUgXCJbQS1aYS16MC05XC1fXC4vXSpcIiwgbGluZSBbMC05XSssIGluCVB5dGhvbglDZXJ0YWluCUhpZ2gKXC5yYjpbMC05XSs6aW4JUnVieQlDZXJ0YWluCUhpZ2gKXC5zY2FsYTpbMC05XSsJU2NhbGEJQ2VydGFpbglIaWdoClwoZ2VuZXJhdGVkIGJ5IHdhaXRyZXNzXCkJV2FpdHJlc3MgUHl0aG9uIHNlcnZlcglDZXJ0YWluCUhpZ2gKMTMyMTIwYzh8MzhhZDUyZmF8MzhjZjAxM2R8MzhjZjAyNTl8MzhjZjAyNWF8MzhjZjAyNWJ8MzhjZjAyNWN8MzhjZjAyNWR8MzhjZjAyNWV8MzhjZjAyNWZ8MzhjZjA0MjF8MzhjZjA0MjR8MzhjZjA0MjV8MzhjZjA0Mjd8MzhjZjA0Mjh8MzhjZjA0MzJ8MzhjZjA0MzR8MzhjZjA0Mzd8MzhjZjA0Mzl8MzhjZjA0NDJ8MzhjZjA3YWF8MzhjZjA4Y2N8MzhjZjA0ZDd8MzhjZjA0YzZ8d2Vic2VhbGVycm9yCVdlYlNFQUwJQ2VydGFpbglIaWdoClwuZ3Jvb3Z5OlswLTldKwlHcm9vdnkJQ2VydGFpbglIaWdoClwubGFuZ1wuKFtBLVphLXowLTlfXSkrXC4oW0EtWmEtejAtOV9dKylFeGNlcHRpb24JSmF2YQlGaXJtCUhpZ2gKXC5sYW5nXC4oW0EtWmEtejAtOV9dKylFeGNlcHRpb24JSmF2YQlGaXJtCUhpZ2gKVW5jbG9zZWQgcXVvdGF0aW9uIG1hcmsJTWljcm9zb2Z0IFNRTCBTZXJ2ZXIJQ2VydGFpbglIaWdoCnF1b3RlZCBzdHJpbmcgbm90IHByb3Blcmx5IHRlcm1pbmF0ZWQJT3JhY2xlCUNlcnRhaW4JSGlnaApEQiBFcnJvcjoJTWFyaWEJQ2VydGFpbglIaWdoCkVycm9yOiBVbmtub3duIGNvbHVtbglNeVNRTAlDZXJ0YWluCUhpZ2gKV2FybmluZy4qbXlzcWxfLioJTXlTUUwJQ2VydGFpbglNZWRpdW0KdmFsaWQgTXlTUUwgcmVzdWx0CU15U1FMCUNlcnRhaW4JSGlnaApNeVNxbENsaWVudFwuCU15U1FMCUNlcnRhaW4JSGlnaApjb21cLm15c3FsXC5qZGJjXC5leGNlcHRpb25zCU15U1FMCUNlcnRhaW4JSGlnaAp3YXJuaW5nIG15c3FsXwlNeVNRTAlDZXJ0YWluCUhpZ2gKd2FybmluZy4qbXNzcWxfLioJTWljcm9zb2Z0IFNRTCBTZXJ2ZXIJQ2VydGFpbglIaWdoCkRyaXZlci4qIFNRTFstX10qU2VydmVyCU1pY3Jvc29mdCBTUUwgU2VydmVyCUNlcnRhaW4JSGlnaAooXFd8XEEpU1FMIFNlcnZlci4qRHJpdmVyCU1pY3Jvc29mdCBTUUwgU2VydmVyCUNlcnRhaW4JSGlnaApDb252ZXJzaW9uIGZhaWxlZCB3aGVuIGNvbnZlcnRpbmcgdGhlCU1pY3Jvc29mdCBTUUwgU2VydmVyCUNlcnRhaW4JSGlnaAoxMDYyIER1cGxpY2F0ZSBlbnRyeQlNWVNRTAlDZXJ0YWluCUhpZ2gKUG9zdGdyZVNRTC4qRVJST1IJUG9zdGdyZVNRTAlDZXJ0YWluCUhpZ2gKV2FybmluZy4qXFdwZ18uKglQb3N0Z3JlU1FMCUNlcnRhaW4JSGlnaAp2YWxpZCBQb3N0Z3JlU1FMIHJlc3VsdAlQb3N0Z3JlU1FMCUNlcnRhaW4JSGlnaApOcGdzcWxcLglQb3N0Z3JlU1FMCUNlcnRhaW4JSGlnaApvcmdcLnBvc3RncmVzcWxcLnV0aWxcLlBTUUxFeGNlcHRpb24JUG9zdGdyZVNRTAlDZXJ0YWluCUhpZ2gKXGJPUkEtWzAtOV1bMC05XVswLTldWzAtOV0JT3JhY2xlCUNlcnRhaW4JSGlnaApPcmFjbGUuKkRyaXZlcl0JT3JhY2xlCUNlcnRhaW4JSGlnaApXYXJuaW5nLipcV29jaV8uKglPcmFjbGUJQ2VydGFpbglIaWdoCldhcm5pbmcuKlxXb3JhXy4qCU9yYWNsZQlDZXJ0YWluCUhpZ2gKV2FybmluZzogb2NpX3BhcnNlKCkJT3JhY2xlCUNlcnRhaW4JSGlnaApDTEkgRHJpdmVyLipEQjIJREIyCUNlcnRhaW4JSGlnaApEQjIgU1FMIGVycm9yCURCMglDZXJ0YWluCUhpZ2gKZGIyX1x3K1woCURCMglDZXJ0YWluCUhpZ2gKXGJkYjJfXHcrXCgJREIyCUNlcnRhaW4JSGlnaApTUUxpdGUvSkRCQ0RyaXZlcglTUUxpdGUJQ2VydGFpbglIaWdoClNRTGl0ZS5FeGNlcHRpb24JU1FMaXRlCUNlcnRhaW4JSGlnaApTeXN0ZW0uRGF0YS5TUUxpdGUuU1FMaXRlRXhjZXB0aW9uCVNRTGl0ZQlDZXJ0YWluCUhpZ2gKV2FybmluZy4qc3FsaXRlXy4qCVNRTGl0ZQlDZXJ0YWluCUhpZ2gKV2FybmluZy4qU1FMaXRlMzo6CVNRTGl0ZQlDZXJ0YWluCUhpZ2gKXFtTUUxJVEVfRVJST1JcXQlTUUxpdGUJQ2VydGFpbglIaWdoCig/aSlXYXJuaW5nLipzeWJhc2UuKglTeWJhc2UJQ2VydGFpbglIaWdoClN5YmFzZSBtZXNzYWdlCVN5YmFzZQlDZXJ0YWluCUhpZ2gKU3liYXNlLipTZXJ2ZXIgbWVzc2FnZS4qCVN5YmFzZQlDZXJ0YWluCUhpZ2gKXFtmdW5jdGlvbi5pYmFzZS5xdWVyeVxdCUZpcmViaXJkCUNlcnRhaW4JSGlnaApEeW5hbWljIFNRTCBFcnJvcglGaXJlYmlyZAlDZXJ0YWluCUhpZ2gKV2FybmluZy4qaWJhc2VfLioJRmlyZWJpcmQJQ2VydGFpbglIaWdoCkV4Y2VwdGlvbi4qSW5mb3JtaXgJSW5mb3JtaXgJQ2VydGFpbglIaWdoClNRTCBlcnJvci4qUE9TKFswLTldKykuKglTQVAgTWF4REIJQ2VydGFpbglIaWdoCldhcm5pbmcuKm1heGRiLioJU0FQIE1heERCCUNlcnRhaW4JSGlnaApXYXJuaW5nLippbmdyZV8JSW5ncmVzIERCCUNlcnRhaW4JSGlnaApJbmdyZXMgU1FMU1RBVEUJSW5ncmVzIERCCUNlcnRhaW4JSGlnaApJbmdyZXNcVy4qRHJpdmVyCUluZ3JlcyBEQglDZXJ0YWluCUhpZ2gKSFNRTERCCUluZ3JlcyBEQglDZXJ0YWluCUhpZ2gKb3JnXC5oc3FsZGJcLmpkYmMJSHlwZXJTUUwJQ2VydGFpbglIaWdoCigoW1woXCksIGEtekEtWjAtOV8tXSo6KXs1fShcL1thLXpBLVowLTlfLV0qKSs6KFwvW2EtekEtWjAtOV8tXSopK1tcclxuXT8pKwlGaWxlIEluamVjdGlvbglDZXJ0YWluCUhpZ2g="
ERROR_MSG = base64.b64decode(ERROR_MSG)
OpenRedirect_Link = "https://google.com"

class BurpExtender(IBurpExtender, IProxyListener, IHttpListener, ITab, IMessageEditorController, AbstractTableModel):
    
      
    def	registerExtenderCallbacks(self, callbacks):
        # keeping a reference to our callbacks object
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        # set our extension name
        callbacks.setExtensionName("BurpErrorNotifier")
        
        # create the log and a lock on which to synchronize when adding log entries
        self._log = ArrayList()
        self._lock = Lock()
        
        # main split pane
        self._splitpane = JSplitPane(JSplitPane.VERTICAL_SPLIT)
        
        #Add clear button
        clearButton = JButton("Clear Log")
        
        # Register the button click event listener
        #clearButton.addActionListener(ActionListener(self.clear_log_table))
        
        self._splitpane.setTopComponent(clearButton)

        # table of log entries
        logTable = Table(self)
        scrollPane = JScrollPane(logTable)
        self._splitpane.setLeftComponent(scrollPane)

        # tabs with request/response viewers
        tabs = JTabbedPane()
        self._requestViewer = callbacks.createMessageEditor(self, False)
        self._responseViewer = callbacks.createMessageEditor(self, False)
        tabs.addTab("Request", self._requestViewer.getComponent())
        tabs.addTab("Response", self._responseViewer.getComponent())
        self._splitpane.setRightComponent(tabs)
        
        # customize our UI components
        callbacks.customizeUiComponent(self._splitpane)
        callbacks.customizeUiComponent(clearButton)
        callbacks.customizeUiComponent(logTable)
        callbacks.customizeUiComponent(scrollPane)
        callbacks.customizeUiComponent(tabs)
        
        # add the custom tab to Burp's UI
        callbacks.addSuiteTab(self)

       

        # obtain our output stream
        self._stdout = PrintWriter(callbacks.getStdout(), True)

        # register ourselves as a Proxy listener
        callbacks.registerProxyListener(self)
        self._stdout.println("Extension is Loaded")

        # register ourselves as an HTTP listener
        callbacks.registerHttpListener(self)
        

    #
    # implement ITab
    #
    
    def getTabCaption(self):
        
        return "BurpErrorNotifier"
    
    def getUiComponent(self):
        return self._splitpane


    #
    # Implement clearing Table
    #

    def clear_log_table(self, event):
        self._lock.acquire()
        self._log.clear()
        self.fireTableDataChanged()
        self._lock.release()
    

    #
    # implement IProxyListener
    #
   

    def processProxyMessage(self, messageIsRequest, message):
        #self._stdout.println(
        #                ("Proxy request to " if messageIsRequest else "Proxy response from ") +
        #                message.getMessageInfo().getHttpService().toString())

        messageInfo=message.getMessageInfo()
        
        if messageIsRequest:
            requestString = messageInfo.getRequest().tostring()    
                

 
    #
    # implement IHttpListener
    #
    
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        # only process requests
        
        request_thread = threading.Thread(target=self.thread_processHttpMessage, args=(toolFlag,messageIsRequest,messageInfo,))
        request_thread.start()
       
            

    def thread_processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        
        global XSS_payload, penRedirect_Link, ERROR_MSG

        # only process requests
        if messageIsRequest:
            return

        
        analyzed = self._helpers.analyzeRequest(messageInfo)
        responseInfo = self._helpers.analyzeResponse(messageInfo.getResponse())
        msgResponse  = self._helpers.bytesToString(messageInfo.getResponse()[responseInfo.getBodyOffset():])

        headers = responseInfo.getHeaders()


        # Add 500 error code
        if(str(responseInfo.getStatusCode()) == "500" and self._callbacks.isInScope(analyzed.getUrl())):
            self._lock.acquire()
            row = self._log.size()
            self._log.add(LogEntry("[SERVER_SIDE] ERROR", self._callbacks.saveBuffersToTempFiles(messageInfo), self._helpers.analyzeRequest(messageInfo).getUrl()))
            self.fireTableRowsInserted(row, row)
            self._lock.release()
            issue = CustomIssue(
                        BasePair=messageInfo,
                        IssueName='Internal ERROR [BurpErrorNotifier]',
                        IssueDetail="Internal error has been found in this request; please check",
                        Severity='Medium',
                        Confidence='Certain'
                    )
            self._callbacks.addScanIssue(issue)

        # Add 302 improper redirection
        if( re.search("302", str(responseInfo.getStatusCode())) and self._callbacks.isInScope(analyzed.getUrl())  ) :

            for head in headers:
                
                if("location:" in head.encode("utf-8").lower() ):
             
                    if(OpenRedirect_Link.lower() in head.encode("utf-8").lower()):
                        self._lock.acquire()
                        row = self._log.size()
                        self._log.add(LogEntry("[Open Redirect] ERROR", self._callbacks.saveBuffersToTempFiles(messageInfo), self._helpers.analyzeRequest(messageInfo).getUrl()))
                        self.fireTableRowsInserted(row, row)
                        self._lock.release()
                        issue = CustomIssue(
                                    BasePair=messageInfo,
                                    IssueName='Open Redirect [BurpErrorNotifier]',
                                    IssueDetail="Open redirection",
                                    Severity='High',
                                    Confidence='Certain'
                                )
                        self._callbacks.addScanIssue(issue)
                    elif ( len(msgResponse) > 0):
                        self._lock.acquire()
                        row = self._log.size()
                        self._log.add(LogEntry("[Improper redirection] ERROR", self._callbacks.saveBuffersToTempFiles(messageInfo), self._helpers.analyzeRequest(messageInfo).getUrl()))    
                        self.fireTableRowsInserted(row, row)
                        self._lock.release()
                        issue = CustomIssue(
                                    BasePair=messageInfo,
                                    IssueName='Improper Redirect [BurpErrorNotifier]',
                                    IssueDetail="Improper redirection",
                                    Severity='Medium',
                                    Confidence='Certain'
                                )
                        self._callbacks.addScanIssue(issue)

        
        # Add XSS discovery

        if( XSS_payload in msgResponse and self._callbacks.isInScope(analyzed.getUrl())) :
            self._lock.acquire()
            row = self._log.size()
            self._log.add(LogEntry("[XSS] ERROR", self._callbacks.saveBuffersToTempFiles(messageInfo), self._helpers.analyzeRequest(messageInfo).getUrl()))
            self.fireTableRowsInserted(row, row)
            self._lock.release()
            issue = CustomIssue(
                        BasePair=messageInfo,
                        IssueName='XSS [BurpErrorNotifier]',
                        IssueDetail="Potential XSS vulnerability",
                        Severity='High',
                        Confidence='Certain'
                    )
            self._callbacks.addScanIssue(issue)

        # Add Error discovery
        
        for err in ERROR_MSG.split("\n"):
            
            pattern = err.split("\t")[0]
            source = err.split("\t")[1]
            confidence = err.split("\t")[2]
            severity = err.split("\t")[3]
            if (re.search(pattern, msgResponse) and self._callbacks.isInScope(analyzed.getUrl())):
                self._lock.acquire()
                row = self._log.size()
                self._log.add(LogEntry("["+source+"] ERROR", self._callbacks.saveBuffersToTempFiles(messageInfo), self._helpers.analyzeRequest(messageInfo).getUrl()))
                self.fireTableRowsInserted(row, row)
                self._lock.release()
                issue = CustomIssue(
                            BasePair=messageInfo,
                            IssueName=source+' ERROR [BurpErrorNotifier]',
                            IssueDetail=source+" error has been found in this request",
                            Severity=severity,
                            Confidence=confidence
                        )
                self._callbacks.addScanIssue(issue)

    #
    # extend AbstractTableModel
    #
    
    def getRowCount(self):
        try:
            return self._log.size()
        except:
            return 0

    def getColumnCount(self):
        return 2

    def getColumnName(self, columnIndex):
        if columnIndex == 0:
            return "Possible vulnerability"
        if columnIndex == 1:
            return "URL"
        return ""

    def getValueAt(self, rowIndex, columnIndex):
        logEntry = self._log.get(rowIndex)
        if columnIndex == 0:
            #return self._callbacks.getToolName(logEntry._tool)
            return logEntry._tool
        if columnIndex == 1:
            return logEntry._url.toString()
        return ""



    #
    # implement IMessageEditorController
    # this allows our request/response viewers to obtain details about the messages being displayed
    #
    
    def getHttpService(self):
        return self._currentlyDisplayedItem.getHttpService()

    def getRequest(self):
        return self._currentlyDisplayedItem.getRequest()

    def getResponse(self):
        return self._currentlyDisplayedItem.getResponse()

#
# extend JTable to handle cell selection
#
    
class Table(JTable):
    def __init__(self, extender):
        self._extender = extender
        self.setModel(extender)
    
    def changeSelection(self, row, col, toggle, extend):
    
        # show the log entry for the selected row
        logEntry = self._extender._log.get(row)
        self._extender._requestViewer.setMessage(logEntry._requestResponse.getRequest(), True)
        self._extender._responseViewer.setMessage(logEntry._requestResponse.getResponse(), False)
        self._extender._currentlyDisplayedItem = logEntry._requestResponse
        
        JTable.changeSelection(self, row, col, toggle, extend)
    
#
# class to hold details of each log entry
#

class LogEntry:
    def __init__(self, tool, requestResponse, url):
        self._tool = tool
        self._requestResponse = requestResponse
        self._url = url
 



class CustomIssue(IScanIssue):

    def __init__(self, BasePair, Confidence='Certain', IssueBackground=None, IssueDetail=None, IssueName='BurpErrorNotifier generated issue', RemediationBackground=None, RemediationDetail=None, Severity='High'):

        self.HttpMessages=[BasePair] # list of HTTP Messages
        self.HttpService=BasePair.getHttpService() # HTTP Service
        self.Url=BasePair.getUrl() # Java URL
        self.Confidence = Confidence # "Certain", "Firm" or "Tentative"
        self.IssueBackground = IssueBackground # String or None
        self.IssueDetail = IssueDetail # String or None
        self.IssueName = IssueName # String
        self.IssueType = 134217728 # always "extension generated"
        self.RemediationBackground = RemediationBackground # String or None
        self.RemediationDetail = RemediationDetail # String or None
        self.Severity = Severity # "High", "Medium", "Low", "Information" or "False positive"

    def getHttpMessages(self):

        return self.HttpMessages

    def getHttpService(self):

        return self.HttpService

    def getUrl(self):

        return self.Url

    def getConfidence(self):

        return self.Confidence

    def getIssueBackground(self):

        return self.IssueBackground

    def getIssueDetail(self):

        return self.IssueDetail

    def getIssueName(self):

        return self.IssueName

    def getIssueType(self):

        return self.IssueType

    def getRemediationBackground(self):

        return self.RemediationBackground

    def getRemediationDetail(self):

        return self.RemediationDetail

    def getSeverity(self):

        return self.Severity