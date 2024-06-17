package widgets.General.EscapeMenu.menus
{
   import flash.display.DisplayObject;
   import flash.geom.Point;
   import flash.geom.Rectangle;
   import gamedata.Gameplay.Persistence.GameSaveLockUnlock;
   import gamedata.Gameplay.shared.GameplayStateData;
   import gamedata.TutorialTip.TutorialMode;
   import olympus.constants.ActionCodes;
   import olympus.constants.DialogTypes;
   import olympus.constants.GameStates;
   import olympus.events.PushButtonEvent;
   import olympus.gamepad.EnterParams;
   import olympus.gamepad.NavManager;
   import olympus.gui.buttons.TextButton;
   import olympus.input.IInputFocusable;
   import olympus.input.InputAction;
   import olympus.input.InputTrigger;
   import olympus.input.adapters.BidirectionalGroupAdapter;
   import olympus.input.adapters.InputAdapterConfirmEvent;
   import olympus.io.CommunicationManager;
   import olympus.localization.Keys;
   import olympus.utils.DisplayObjectUtils;
   import olympus.utils.SystemUtils;
   import olympus.utils.WidgetUtils;
   import widgets.General.EscapeMenu.EscapeMenuTunables;
   import widgets.General.EscapeMenu.controls.EscMenuAlertTextButton;
   import widgets.shared.constants.TelemetryConstants;
   import widgets.shared.data.CDSStateData;
   import widgets.shared.utils.SharedTutorialUtils;
   
   [Embed(source="/_assets/assets.swf", symbol="widgets.General.EscapeMenu.menus.Sims4EscapeMenu")]
   public final class Sims4EscapeMenu extends EscapeMenu implements IInputFocusable
   {
       
      
      public var btnUltimateUX:TextButton;
      
      public var btnSave:TextButton;
      
      public var btnSaveAs:TextButton;
      
      public var btnCredits:TextButton;
      
      public var btnMainMenu:TextButton;
      
      public var btnAchievements:TextButton;
      
      public var btnEditWorld:TextButton;
      
      public var btnPatchNotes:TextButton;
      
      public var btnEndTutorial:TextButton;
      
      public var mMenuInput:BidirectionalGroupAdapter;
      
      public function Sims4EscapeMenu()
      {
         super();
      }
      
      protected function splitStringIntoChunks(inputString:String, chunkSize:int) : Array
      {
         var result:Array = new Array();
         while(inputString.length > 0)
         {
            var chunk:String = inputString.substr(0,chunkSize);
            result.push(chunk);
            inputString = inputString.substr(chunkSize);
         }
         return result;
      }
      
      override protected function Setup() : void
      {
         var _loc1_:Array;
         var _loc2_:uint;
         var _loc3_:CDSStateData;
         var _loc4_:EscMenuAlertTextButton;
         var chunks:Array;
         var i:int;
         super.Setup();
         this.btnSave.htmlText = Keys.GENERIC_SAVE.toString();
         this.btnSaveAs.htmlText = SystemUtils.UsingConsoleInputMode ? Keys.GENERIC_SAVE.toString() : Keys.ESCAPE_MENU_SAVE_AS.toString();
         this.btnCredits.htmlText = Keys.OPTIONS_CREDITS.toString();
         this.btnMainMenu.htmlText = Keys.ESCAPE_MENU_EXIT_TO_MAIN_MENU.toString();
         this.btnAchievements.htmlText = Keys.ESCAPE_MENU_ACHIEVEMENTS.toString();
         this.btnEditWorld.htmlText = Keys.ESCAPE_MENU_EDIT_WORLD.toString();
         this.btnPatchNotes.htmlText = Keys.ESCAPE_MENU_PATCH_NOTES.toString();
         this.btnEndTutorial.htmlText = Keys.ESCAPE_MENU_END_TUTORIAL.toString();
         this.btnSave.addEventListener(PushButtonEvent.CLICK,this.OnSaveClick,false,0,true);
         this.btnSaveAs.addEventListener(PushButtonEvent.CLICK,this.OnSaveAsClick,false,0,true);
         this.btnCredits.addEventListener(PushButtonEvent.CLICK,this.OnCreditsClick,false,0,true);
         this.btnMainMenu.addEventListener(PushButtonEvent.CLICK,this.OnMainMenuClick,false,0,true);
         this.btnAchievements.addEventListener(PushButtonEvent.CLICK,this.OnAchievementsClick,false,0,true);
         this.btnEditWorld.addEventListener(PushButtonEvent.CLICK,this.OnEditWorldClick,false,0,true);
         this.btnPatchNotes.addEventListener(PushButtonEvent.CLICK,this.OnShowPatchNotesButtonClick,false,0,true);
         this.btnEndTutorial.addEventListener(PushButtonEvent.CLICK,this.OnEndTutorialClick,false,0,true);
         try
         {
            this.btnUltimateUX.htmlText = "Ultimate UX";
            this.btnUltimateUX.addEventListener(PushButtonEvent.CLICK,this.OnUltimateUXClick,false,0,true);
            _loc1_ = [this.btnSave,this.btnSaveAs,btnOptions,this.btnUltimateUX,btnHelp,btnLessons,this.btnPatchNotes,this.btnCredits,this.btnAchievements,this.btnEditWorld,this.btnMainMenu];
         }
         catch(e:Error)
         {
            _loc1_ = [this.btnSave,this.btnSaveAs,btnOptions,btnHelp,btnLessons,this.btnPatchNotes,this.btnCredits,this.btnAchievements,this.btnEditWorld,this.btnMainMenu];
            chunks = this.splitStringIntoChunks(e.toString(),26);
            i = 0;
            while(i < chunks.length)
            {
               if(_loc1_[i])
               {
                  _loc1_[i].htmlText = chunks[i];
               }
               i++;
            }
         }
         _loc2_ = CommunicationManager.CallGameService("GetGameState") as uint;
         if(TutorialMode.IsFTUE() && _loc2_ != GameStates.CAS)
         {
            this.btnEndTutorial.visible = true;
            _loc1_.push(this.btnEndTutorial);
         }
         else
         {
            this.btnEndTutorial.visible = false;
         }
         this.PositionButtons(_loc1_);
         _loc3_ = new CDSStateData(CommunicationManager.CallGameService("GetCDSState"));
         if(_loc4_ = btnOptions as EscMenuAlertTextButton)
         {
            _loc4_.ShowAlert(_loc3_.requiresInteraction);
         }
         CommunicationManager.AddMessageListener("CDSState",this.CDSStateMessageHandler,this);
         CommunicationManager.AddMessageListener("GameSaveLockUnlock",this.HandleGameSaveLockUnlock,this,GameSaveLockUnlock);
         if(SystemUtils.UsingConsoleInputMode)
         {
            this.InitGamepad();
         }
      }
      
      protected function PositionButtons(param1:Array) : void
      {
         if(!param1 || param1.length == 0)
         {
            return;
         }
         var _loc2_:DisplayObject = param1[0];
         var _loc3_:Number = escapeMenuPanelBase.height;
         var _loc4_:Rectangle = DisplayObjectUtils.StackMultiple(param1,EscapeMenuTunables.ESCAPE_MENU_BUTTON_MARGINS,true,0,null,new Point(_loc2_.x,_loc2_.y),null);
         btnQuit.y = _loc4_.y + _loc4_.height + EscapeMenuTunables.ESCAPE_MENU_EXIT_SPACING;
         escapeMenuPanelBase.height = btnQuit.y + btnQuit.height + EscapeMenuTunables.ESCAPE_MENU_BOTTOM_SPACING;
         this.y = (_loc3_ - escapeMenuPanelBase.height) / 2;
      }
      
      override public function CanBeShown(param1:Object = null) : Boolean
      {
         var _loc2_:uint = 0;
         var _loc4_:* = false;
         _loc2_ = CommunicationManager.CallGameService("GetGameState") as uint;
         var _loc3_:Boolean = _loc2_ == GameStates.MAIN_MENU || _loc2_ == GameStates.ENTER_MAIN_MENU;
         this.btnMainMenu.enabled = !_loc3_;
         _loc4_ = _loc2_ == GameStates.PLAY;
         this.btnAchievements.enabled = _loc4_;
         this.btnAchievements.TooltipExt.SetText(!_loc4_ ? Keys.ESCAPE_MENU_ACHIEVEMENTS_DISABLED : null);
         this.HandleGameSaveLockUnlock(GameplayStateData.SaveLockUnlockMessage);
         return super.CanBeShown(param1);
      }
      
      protected function OnEndTutorialClick(param1:PushButtonEvent) : void
      {
         CommunicationManager.SendUIMessage("HideEscapeMenu");
         SharedTutorialUtils.ShowEndTutorialConfirmationDialog(SharedTutorialUtils.FTUE_END_FROM_ESC_MENU);
      }
      
      protected function OnSaveClick(param1:PushButtonEvent) : void
      {
         CommunicationManager.SendUIMessage("SaveCurrentGame");
         CommunicationManager.SendUIMessage("HideEscapeMenu");
      }
      
      protected function OnSaveAsClick(param1:PushButtonEvent) : void
      {
         if(SystemUtils.UsingConsoleInputMode)
         {
            CommunicationManager.SendUIMessage("ShowSaveLoadConsoleMenu",{"isSaving":true});
         }
         else
         {
            CommunicationManager.SendUIMessage("ShowSaveLoadMenu",{"isSaving":true});
         }
      }
      
      protected function OnCreditsClick(param1:PushButtonEvent) : void
      {
         CommunicationManager.SendUIMessage("ShowGameCredits");
      }
      
      protected function OnMainMenuClick(param1:PushButtonEvent) : void
      {
         CommunicationManager.SendUIMessage("ShowExitToMainMenuDialog");
      }
      
      protected function OnAchievementsClick(param1:PushButtonEvent) : void
      {
         CommunicationManager.SendUIMessage("ShowAchievements");
      }
      
      protected function OnShowPatchNotesButtonClick(param1:PushButtonEvent) : void
      {
         var _loc2_:String = CommunicationManager.CallGameService("GetPatchNotesURL") as String;
         CommunicationManager.SendUIMessage("OpenExternalURL",{"url":_loc2_});
      }
      
      protected function OnEditWorldClick(param1:PushButtonEvent) : void
      {
         CommunicationManager.SendUIMessage("ShowExitToManageWorldsDialog",{"context":TelemetryConstants.GE_MANAGE_WORLD_ESCAPE_MENU});
      }
      
      protected function OnUltimateUXClick(param1:PushButtonEvent) : void
      {
         CommunicationManager.SendUIMessage("ShowDialog",{
            "type":DialogTypes.CUSTOM,
            "title":"Ultimate UX",
            "description":"Ultimate UX Settings."
         });
      }
      
      protected function HandleGameSaveLockUnlock(param1:GameSaveLockUnlock) : void
      {
         var _loc2_:uint = 0;
         var _loc3_:* = false;
         if(Boolean(param1) && param1.is_locked)
         {
            this.btnSave.enabled = false;
            this.btnSave.TooltipExt.SetText(param1.lock_reason);
            this.btnSaveAs.enabled = false;
            this.btnSaveAs.TooltipExt.SetText(param1.lock_reason);
            if(this.btnEditWorld.enabled)
            {
               this.btnEditWorld.enabled = false;
               this.btnEditWorld.TooltipExt.SetText(param1.lock_reason);
            }
            return;
         }
         _loc2_ = CommunicationManager.CallGameService("GetGameState") as uint;
         _loc3_ = _loc2_ == GameStates.CAS;
         var _loc4_:Boolean = _loc2_ == GameStates.MAIN_MENU || _loc2_ == GameStates.ENTER_MAIN_MENU || _loc3_;
         this.btnSave.enabled = !_loc4_;
         this.btnSave.TooltipExt.SetText(null);
         this.btnSaveAs.enabled = !_loc4_;
         this.btnSaveAs.TooltipExt.SetText(null);
         var _loc5_:Boolean = _loc2_ == GameStates.PLAY || _loc2_ == GameStates.BUILD;
         var _loc6_:* = CommunicationManager.CallGameService("GetNumHouseholds") as uint > 0;
         if(TutorialMode.IsFTUE())
         {
            this.btnEditWorld.enabled = false;
            this.btnEditWorld.TooltipExt.SetText(Keys.ESCAPE_MENU_EDIT_WORLD_DISABLED_FTUE);
         }
         else if(!_loc5_ && !_loc3_)
         {
            this.btnEditWorld.enabled = false;
            this.btnEditWorld.TooltipExt.SetText(Keys.ESCAPE_MENU_EDIT_WORLD_DISABLED_TOOLTIP);
         }
         else if(_loc3_ && !_loc6_)
         {
            this.btnEditWorld.enabled = false;
            this.btnEditWorld.TooltipExt.SetText(Keys.ESCAPE_MENU_EDIT_WORLD_DISABLED_HOUSEHOLD);
         }
         else if(_loc5_ && GameplayStateData.IsBlockingSituationRunning)
         {
            this.btnEditWorld.enabled = false;
            this.btnEditWorld.TooltipExt.SetText(Keys.ESCAPE_MENU_EDIT_WORLD_DISABLED_BY_EVENT);
         }
         else
         {
            this.btnEditWorld.enabled = true;
            this.btnEditWorld.TooltipExt.SetText(null);
         }
      }
      
      protected function CDSStateMessageHandler(param1:Object) : void
      {
         var _loc3_:CDSStateData = null;
         var _loc2_:EscMenuAlertTextButton = btnOptions as EscMenuAlertTextButton;
         if(_loc2_)
         {
            _loc3_ = new CDSStateData(param1);
            _loc2_.ShowAlert(_loc3_.requiresInteraction);
         }
      }
      
      protected function InitGamepad() : void
      {
         var _loc2_:Number = NaN;
         var _loc4_:DisplayObject = null;
         var _loc5_:DisplayObject = null;
         this.btnSave.visible = false;
         btnHelp.visible = false;
         this.btnPatchNotes.visible = false;
         this.btnAchievements.visible = false;
         btnQuit.visible = false;
         var _loc1_:Vector.<DisplayObject> = new <DisplayObject>[this.btnSaveAs,btnOptions,btnLessons,this.btnCredits,this.btnEditWorld];
         if(this.btnEndTutorial.visible)
         {
            _loc1_.push(this.btnEndTutorial);
         }
         _loc1_.push(this.btnMainMenu);
         this.mMenuInput = new BidirectionalGroupAdapter(_loc1_);
         this.mMenuInput.OnBackCall(this.OnInputBack);
         this.mMenuInput.OnConfirmCall(this.HandleButtonPress);
         this.mMenuInput.AddInputAction(InputAction.WhenTriggered(InputTrigger.FromActionCode(ActionCodes.TOGGLE_MAIN_MENU)).CallFunction(this.OnInputBack).AllowWhileModalOpen(true).SetLegendKey(Keys.GENERIC_BACK));
         _loc2_ = escapeMenuPanelBase.height;
         var _loc3_:Number = EscapeMenuTunables.FIRST_BUTTON_Y_LOC;
         for each(_loc5_ in _loc1_)
         {
            if(_loc5_.visible)
            {
               _loc5_.y = _loc3_;
               _loc3_ += EscapeMenuTunables.SPACING_BETWEEN_BUTTON_Y_LOC;
               _loc4_ = _loc5_;
            }
         }
         _loc4_.y += EscapeMenuTunables.ESCAPE_MENU_EXIT_SPACING;
         _loc3_ += EscapeMenuTunables.ESCAPE_MENU_EXIT_SPACING;
         escapeMenuPanelBase.height = _loc3_ + EscapeMenuTunables.VERTICAL_MARGIN;
         this.y = (_loc2_ - escapeMenuPanelBase.height) / 2;
      }
      
      public function HandleButtonPress(param1:InputAdapterConfirmEvent) : void
      {
         switch(param1.GetObjName())
         {
            case this.btnCredits.name:
               NavManager.Instance.FocusWidgetForward("GameCredits");
               break;
            case btnOptions.name:
               NavManager.Instance.FocusWidgetForward("OptionsMenu");
         }
      }
      
      public function Enter(param1:EnterParams = null) : IInputFocusable
      {
         if(param1 == null || param1.mArgs == null || param1.mArgs.bIsSaving == false)
         {
            this.mMenuInput.Enter(param1);
         }
         return this;
      }
      
      public function Exit() : void
      {
         this.mMenuInput.Exit();
      }
      
      protected function OnInputBack() : void
      {
         CommunicationManager.SendUIMessage("Hide" + WidgetUtils.GetBaseName(this));
      }
   }
}
